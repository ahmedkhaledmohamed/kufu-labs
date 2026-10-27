# SPDX-License-Identifier: GPL-3.0-only
"""Build an offline demo from the actual pinned CPU FilterPipeline, not a port."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import itertools
import json
import math
import platform
import sys
import types
import urllib.request
from pathlib import Path

REVISION = "a2b97fe0a7d908813f0d555df284307fd5060fd5"
ROOT = Path(__file__).resolve().parent
FILES = [
    "sleap_nn/inference/filters.py",
    "sleap_nn/inference/outputs.py",
    "sleap_nn/inference/preprocess_info.py",
    "LICENSE",
]


def load_oracle(source):
    """Bypass eager predictor package initializers, never the actual numerical modules."""
    expected = json.loads((ROOT / "source-lock.json").read_text())
    for name in FILES:
        digest = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if digest != expected["sha256"][name]:
            raise ValueError(f"Pinned source mismatch: {name}")
    for name in ["sleap_nn", "sleap_nn.inference"]:
        package = types.ModuleType(name)
        package.__path__ = [str(source / name.replace(".", "/"))]
        sys.modules[name] = package
    return importlib.import_module("sleap_nn.inference.filters")


def fixtures():
    a = [[40, 30], [47, 35], [45, 45], [52, 28], [62, 40], [76, 44]]

    def shifted(dx, dy):
        return [[x + dx, y + dy] for x, y in a]

    flipped = [p[:] for p in a]
    flipped[2], flipped[3] = flipped[3], flipped[2]
    large = [p[:] for p in a]
    large[-1] = [95, 85]
    missing_a = [p if i < 3 else None for i, p in enumerate(a)]
    missing_b = [p if i >= 3 else None for i, p in enumerate(a)]
    return [
        (
            "near-duplicate",
            "Near duplicate",
            "Small displacement, similar shape. Compare a high pairwise score with the actual suppression decision.",
            [a, shifted(1, 1)],
            0.8,
        ),
        (
            "nearby",
            "Nearby, different pose",
            "Constructed as two distinct nearby subjects. Overlapping boxes alone cannot establish identity.",
            [a, [[x + 4, y + 7 + (i % 2) * 3] for i, (x, y) in enumerate(a)]],
            0.5,
        ),
        (
            "flipped",
            "Swapped node labels",
            "Two limb labels are swapped while the bounding box stays the same. Compare IoU with OKS.",
            [a, flipped],
            0.8,
        ),
        (
            "directional",
            "Different scale, same neighbourhood",
            "A distant tail node enlarges A’s box. OKS(A → B) and OKS(B → A) differ. Reverse score order at threshold 0.6.",
            [large, shifted(2, 2)],
            0.6,
        ),
        (
            "missing",
            "Missing / no shared nodes",
            "A and B have disjoint visible node sets. C has no coordinates and is unavailable before filtering, not newly suppressed.",
            [missing_a, missing_b, [None] * 6],
            0.5,
        ),
        (
            "degenerate",
            "Zero-area boxes",
            "Both poses lie on a vertical line. The pinned metrics return zero for these degenerate areas.",
            [
                [[45, 25 + i * 5] for i in range(6)],
                [[45, 26 + i * 5] for i in range(6)],
            ],
            0,
        ),
        (
            "chain",
            "Three-instance context",
            "Neighbouring boxes overlap more than the outer pair. At IoU threshold 0.5, moving B first changes which instances survive.",
            [a, shifted(9, 0), shifted(18, 0)],
            0.5,
        ),
    ]


def generate(source):
    import attrs
    import numpy
    import torch

    torch.set_num_threads(1)
    oracle = load_oracle(source)
    cases, filter_runs, probes = [], 0, 0
    for slug, title, note, poses, default in fixtures():
        n = len(poses)
        coords = torch.tensor(
            [
                [[float("nan"), float("nan")] if p is None else p for p in pose]
                for pose in poses
            ],
            dtype=torch.float32,
            device="cpu",
        )
        valid = ~torch.isnan(coords).all(dim=-1).all(dim=-1)
        metrics = {
            method: [
                [
                    getattr(
                        oracle.FilterPipeline,
                        "_oks" if method == "oks" else "_bbox_iou",
                    )(coords[i], coords[j])
                    for j in range(n)
                ]
                for i in range(n)
            ]
            for method in ["iou", "oks"]
        }
        orders = []
        for order in itertools.permutations(range(n)):
            scores = [0.0] * n
            for rank, i in enumerate(order):
                scores[i] = [0.95, 0.75, 0.55][rank]
            orders.append(
                {
                    "label": " → ".join(chr(65 + i) for i in order),
                    "scores": scores,
                    "id": "".join(str(i) for i in order),
                }
            )
        orders.append(
            {"label": "Equal scores (oracle order)", "scores": [0.8] * n, "id": "tie"}
        )
        for order in orders:
            order["actual_order"] = (
                torch.tensor(order["scores"], dtype=torch.float32, device="cpu")
                .argsort(descending=True)
                .tolist()
            )
        tables = {}
        for method, matrix in metrics.items():
            bounds = sorted(
                {
                    0.0,
                    1.0,
                    *(matrix[i][j] for i in range(n) for j in range(n) if i != j),
                }
            )
            tables[method] = {}
            for order in orders:

                def run(t, coords=coords, order=order, method=method, valid=valid, n=n):
                    nonlocal filter_runs
                    inputs = oracle.Outputs(
                        pred_keypoints=coords.unsqueeze(0).clone(),
                        instance_scores=torch.tensor(
                            [order["scores"]], dtype=torch.float32, device="cpu"
                        ),
                    )
                    before = inputs.pred_keypoints.clone()
                    pipeline = oracle.FilterPipeline(
                        oracle.FilterConfig(
                            overlapping=True,
                            overlapping_method=method,
                            overlapping_threshold=t,
                        )
                    )
                    outputs = pipeline.apply(inputs)
                    # Ensure inspection never mutates the original input.
                    assert torch.allclose(before, inputs.pred_keypoints, equal_nan=True)
                    assert outputs.pred_keypoints.device.type == "cpu"
                    present = ~torch.isnan(outputs.pred_keypoints[0]).all(dim=-1).all(
                        dim=-1
                    )
                    filter_runs += 1
                    return [
                        "unavailable"
                        if not valid[i]
                        else "retained"
                        if present[i]
                        else "suppressed"
                        for i in range(n)
                    ]

                rows = []
                for k, bound in enumerate(bounds):
                    result = run(bound)
                    rows.append({"lower": bound, "states": result})
                    if k + 1 < len(bounds):
                        hi = bounds[k + 1]
                        # Boundaries are actual returned similarities; equality must retain.
                        for t in [
                            (bound + hi) / 2,
                            math.nextafter(hi, bound),
                            math.nextafter(bound, hi),
                        ]:
                            assert run(t) == result, (slug, method, t, result)
                            probes += 1
                tables[method][order["id"]] = rows
        cases.append(
            {
                "id": slug,
                "title": title,
                "note": note,
                "poses": poses,
                "default": default,
                "metrics": metrics,
                "orders": orders,
                "tables": tables,
            }
        )
    # Meaningful contrasting oracle outcomes, independent of UI rendering.
    by_id = {c["id"]: c for c in cases}

    def at(slug, method, order, threshold):
        return [
            r for r in by_id[slug]["tables"][method][order] if r["lower"] <= threshold
        ][-1]["states"]

    assert at("flipped", "iou", "01", 0.8) == ["retained", "suppressed"]
    assert at("flipped", "oks", "01", 0.8) == ["retained", "retained"]
    assert at("chain", "iou", "012", 0.5) == ["retained", "suppressed", "retained"]
    assert at("chain", "iou", "102", 0.5) == ["suppressed", "retained", "suppressed"]
    assert at("directional", "oks", "01", 0.6) != at("directional", "oks", "10", 0.6)
    assert at("missing", "oks", "012", 0.5)[2] == "unavailable"
    manifest = json.loads((ROOT / "source-lock.json").read_text())
    report = {
        "revision": REVISION,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": numpy.__version__,
        "attrs": attrs.__version__,
        "device": "cpu",
        "dtype": "float32",
        "cases": len(cases),
        "filter_runs": filter_runs,
        "interior_and_adjacent_probes": probes,
        "source_sha256": manifest["sha256"],
    }
    data = {
        "cases": cases,
        "report": report,
        "nodes": ["nose", "neck", "left fore", "right fore", "hip", "tail"],
        "edges": [[0, 1], [1, 4], [4, 5], [1, 2], [1, 3]],
    }
    payload = json.dumps(data, allow_nan=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    html = (
        (ROOT / "template.html")
        .read_text()
        .replace("/*__DATA__*/", "const DATA = " + payload + ";")
    )
    (ROOT / "index.html").write_text(html)
    (ROOT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Download only hash-pinned source modules and licence into --source (no model weights).",
    )
    args = parser.parse_args()
    if args.fetch:
        lock = json.loads((ROOT / "source-lock.json").read_text())
        for name, expected in lock["sha256"].items():
            url = (
                f"https://raw.githubusercontent.com/talmolab/sleap-nn/{REVISION}/{name}"
            )
            payload = urllib.request.urlopen(url, timeout=60).read()
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f"Pinned download mismatch: {name}")
            target = args.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    generate(args.source.resolve())

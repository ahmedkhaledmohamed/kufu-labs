# SPDX-License-Identifier: GPL-3.0-only
"""Experimental read-only inspector for the sleap-nn 0.3.4 Labels filter."""

import hashlib
import importlib.metadata
import importlib.util
from functools import lru_cache

import numpy as np
from qtpy import QtCore, QtWidgets
from sleap_io import PredictedInstance


@lru_cache(maxsize=1)
def filter_ops():
    """Load unchanged, hash-verified NumPy ops without model-stack initializers.

    These are private helpers, so this experimental adapter deliberately fails
    closed on a different distribution or source rather than guessing semantics.
    No package namespace or numerical implementation is replaced.
    """
    dist = importlib.metadata.distribution("sleap-nn")
    if dist.version != "0.3.4":
        raise ValueError("This adapter requires sleap-nn 0.3.4.")
    path = dist.locate_file("sleap_nn/inference/ops/filters.py")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != "e09aae412051c4faaa1998d9371a23d78d01140ea1e200573485e65a7fd716d6":
        raise ValueError(
            "The installed overlap source differs from the verified release."
        )
    spec = importlib.util.spec_from_file_location("kufu_verified_overlap_ops", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_pair(a, b):
    """Measure matching host instances without changing any model field."""
    if a is b:
        raise ValueError("Choose two different instances.")
    if a.skeleton is not b.skeleton:
        raise ValueError("Choose instances sharing the same skeleton and node order.")
    points_a, points_b = a.numpy().copy(), b.numpy().copy()
    if np.isinf(points_a).any() or np.isinf(points_b).any():
        raise ValueError(
            "Infinite coordinates are unsupported; inspect the source data."
        )
    ops = filter_ops()
    boxes = [ops._instance_bbox(inst) for inst in (a, b)]
    with np.errstate(invalid="ignore", divide="ignore"):
        iou = float(ops._compute_iou_one_to_many(boxes[0], boxes[1][None])[0])
    valid_a = ~np.isnan(points_a).any(axis=1)
    valid_b = ~np.isnan(points_b).any(axis=1)
    return {
        "iou": iou,
        "oks_ab": ops._compute_oks(points_a, points_b),
        "oks_ba": ops._compute_oks(points_b, points_a),
        "shared_nodes": int((valid_a & valid_b).sum()),
        "valid_nodes": [int(valid_a.sum()), int(valid_b.sum())],
        "degenerate": [bool(np.prod(box[2:] - box[:2]) <= 0) for box in boxes],
    }


def instance_description(index, instance):
    """Keep prediction confidence distinct from human annotations."""
    if isinstance(instance, PredictedInstance):
        return f"{index + 1}: prediction, score {instance.score:.6g}"
    return f"{index + 1}: manual annotation (no prediction score)"


class PairOverlapDialog(QtWidgets.QDialog):
    """Choose two instances in the current host frame; inspect only."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.instances = []
        self.frame = None
        self.setWindowTitle("Pairwise overlap inspector — experimental")
        self.resize(670, 620)
        self.setModal(False)
        layout = QtWidgets.QVBoxLayout(self)
        self.frame_label = QtWidgets.QLabel()
        layout.addWidget(self.frame_label)
        self.choices = []
        for index, name in enumerate(("A", "B")):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(f"Instance {name}"))
            choice = QtWidgets.QComboBox()
            choice.setObjectName(f"instance_{name}")
            choice.currentIndexChanged.connect(self.update_result)
            self.choices.append(choice)
            row.addWidget(choice, stretch=1)
            button = QtWidgets.QPushButton(f"Use canvas selection as {name}")
            button.clicked.connect(lambda checked=False, i=index: self.use_selection(i))
            row.addWidget(button)
            layout.addLayout(row)
        self.result = QtWidgets.QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setObjectName("overlap_result")
        layout.addWidget(self.result, stretch=1)
        note = QtWidgets.QLabel(
            "Backend: sleap-nn 0.3.4 NumPy Labels overlap filter; κ = 0.1. "
            "OKS uses the first instance's box area. This is not the browser "
            "demo's tensor backend. Pair scores do not establish animal identity "
            "or predict the full greedy filter outcome. No labels are changed."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        close = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        close.rejected.connect(self.close)
        layout.addWidget(close)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_frame)
        self.timer.start(400)
        self.refresh_frame()

    def refresh_frame(self):
        """Follow navigation and edits using a dialog-owned timer."""
        frame = self.app.state.get("labeled_frame", default=None)
        instances = list(frame.instances) if frame is not None else []
        changed = frame is not self.frame or [id(x) for x in instances] != [
            id(x) for x in self.instances
        ]
        if changed:
            self.frame, self.instances = frame, instances
            selected = self.app.state.get("instance", default=None)
            selected_index = next(
                (i for i, x in enumerate(instances) if x is selected), 0
            )
            for i, choice in enumerate(self.choices):
                choice.blockSignals(True)
                choice.clear()
                for n, instance in enumerate(instances):
                    choice.addItem(instance_description(n, instance))
                choice.setCurrentIndex(
                    selected_index
                    if i == 0
                    else (selected_index + 1) % max(1, len(instances))
                )
                choice.blockSignals(False)
        for choice in self.choices:
            for n, instance in enumerate(instances):
                choice.setItemText(n, instance_description(n, instance))
        self.frame_label.setText(
            f"Current frame: {frame.frame_idx} (zero-based); {len(instances)} instances"
            if frame is not None
            else "No current labeled frame"
        )
        self.update_result()

    def showEvent(self, event):
        self.timer.start(400)
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def use_selection(self, index):
        selected = self.app.state.get("instance", default=None)
        for n, instance in enumerate(self.instances):
            if instance is selected:
                self.choices[index].setCurrentIndex(n)
                return

    def update_result(self, *args):
        indices = [choice.currentIndex() for choice in self.choices]
        if len(self.instances) < 2 or min(indices) < 0:
            self.result.setPlainText("Open a frame with at least two instances.")
            return
        a, b = [self.instances[i] for i in indices]
        try:
            result = inspect_pair(a, b)
        except (ValueError, ImportError, OSError) as exc:
            self.result.setPlainText(f"Unavailable: {exc}")
            return
        lines = [
            f"Box IoU: {result['iou']:.12g}",
            f"OKS(A → B), scale from A: {result['oks_ab']:.12g}",
            f"OKS(B → A), scale from B: {result['oks_ba']:.12g}",
            f"Shared coordinate-bearing nodes: {result['shared_nodes']}",
            "",
        ]
        if not result["shared_nodes"] or any(result["degenerate"]):
            lines += [
                "Missing shared coordinates or zero-area geometry is present.",
                "A zero metric here is not evidence of different animals.",
                "",
            ]
        lines.append("Node order and stored prediction confidences:")
        for n, node in enumerate(a.skeleton.nodes):
            values = []
            for label, instance in (("A", a), ("B", b)):
                xy = instance.numpy()[n]
                score = (
                    f"{instance.points['score'][n]:.6g}"
                    if isinstance(instance, PredictedInstance)
                    else "not a prediction"
                )
                values.append(f"{label} ({xy[0]:.6g}, {xy[1]:.6g}), score {score}")
            lines.append(f"{node.name}: " + "; ".join(values))
        text = "\n".join(lines)
        if self.result.toPlainText() != text:
            self.result.setPlainText(text)

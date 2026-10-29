# SPDX-License-Identifier: GPL-3.0-only
"""Exercise real SLEAP widgets with constructed, embedded .slp fixtures."""

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import resource
import shutil
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--baseline", action="store_true")
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(output / "matplotlib"))

import numpy as np
import sleap
import sleap_io as sio
from PIL import Image, ImageDraw
from sleap import util


def isolated_config(shortname, ignore_file_not_found=False, get_defaults=False):
    """Isolate preferences only; all host, video, pose and metric code is real."""
    target = output / "preferences" / shortname
    target.parent.mkdir(parents=True, exist_ok=True)
    default = Path(util.get_package_file(f"config/{shortname}"))
    if get_defaults:
        return str(default)
    if not target.exists() and not ignore_file_not_found and default.exists():
        shutil.copyfile(default, target)
    return str(target)


util.get_config_file = isolated_config

from qtpy import QtCore, QtGui, QtTest, QtWidgets
from sleap.gui.app import MainWindow

start = time.perf_counter()
host_revision = subprocess.check_output(
    ["git", "-C", str(Path(sleap.__file__).parent), "rev-parse", "HEAD"], text=True
).strip()
assert host_revision == "d24a98fbc2f69d84c6c080bab4e826c4992ac76f"
qt = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
skeleton = sio.Skeleton(nodes=["head", "neck", "left", "right", "hip", "tail"])
skeleton.add_edges(
    [
        ("head", "neck"),
        ("neck", "left"),
        ("neck", "right"),
        ("neck", "hip"),
        ("hip", "tail"),
    ]
)
a = np.array([[40, 30], [47, 35], [45, 45], [52, 28], [62, 40], [76, 44]], float)
large = a.copy()
large[-1] = [95, 85]
missing_a, missing_b = a.copy(), a.copy()
missing_a[3:] = np.nan
missing_b[:3] = np.nan
cases = [(a, a + 1), (large, a + 2), (missing_a, missing_b)]
image_paths = []
for i in range(len(cases)):
    image = Image.new("RGB", (220, 160), "#f3f5f7")
    ImageDraw.Draw(image).text(
        (8, 140), "Constructed coordinates; no recording", fill="black"
    )
    path = output / f"constructed-{i}.png"
    image.save(path)
    image_paths.append(str(path))
video = sio.Video.from_filename(image_paths)
frames = []
for i, (p, q) in enumerate(cases):
    instances = [
        sio.PredictedInstance.from_numpy(
            pts,
            skeleton,
            point_scores=np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4]),
            score=score,
        )
        for pts, score in ((p, 0.95), (q, 0.59))
    ]
    # A manual annotation is deliberately not given a prediction confidence.
    instances.append(sio.Instance.from_numpy(a + [40, 30], skeleton))
    frames.append(sio.LabeledFrame(video, i, instances))
fixture = output / "constructed.pkg.slp"
sio.save_slp(sio.Labels(frames), fixture, embed=True)
digest_before = hashlib.sha256(fixture.read_bytes()).hexdigest()
labels = sio.load_slp(fixture)


def snapshot(labels):
    """Include coordinates, visibility, completion, confidence and provenance."""
    return [
        (
            type(inst).__name__,
            inst.points.tobytes(),
            getattr(inst, "score", None),
            id(inst.skeleton),
            inst.skeleton.node_names,
            id(inst.from_predicted),
        )
        for frame in labels
        for inst in frame.instances
    ]


window = MainWindow(labels_path=str(fixture), no_usage_data=True)
labels = window.labels
before = snapshot(labels)
assert not window.state["has_changes"]
window.resize(1100, 760)
window.show()
QtTest.QTest.qWait(500)
window.state["video"] = labels.videos[0]
window.state["frame_idx"] = 0
QtTest.QTest.qWait(500)
analyze = next(
    action.menu()
    for action in window.menuBar().actions()
    if action.text().replace("&", "") == "Analyze"
)
menu_actions = [action.text() for action in analyze.actions()]
analyze.popup(window.mapToGlobal(QtCore.QPoint(180, 25)))
QtTest.QTest.qWait(100)
analyze.grab().save(str(output / "analyze-menu.png"))
analyze.hide()
results = {
    "host_revision": host_revision,
    "rendering": "real Qt widgets using the offscreen platform",
    "mode": "baseline" if args.baseline else "patched",
    "versions": {
        name: importlib.metadata.version(name)
        for name in ("sleap", "sleap-io", "sleap-nn", "numpy", "PySide6")
    },
    "analyze_menu": menu_actions,
    "cases": [],
}
window.grab().save(str(output / "host.png"))
if args.baseline:
    assert "Inspect Pairwise Overlap..." not in menu_actions
else:
    from sleap.gui.dialogs.pair_overlap import filter_ops, inspect_pair

    action = next(
        a for a in analyze.actions() if a.text() == "Inspect Pairwise Overlap..."
    )
    action.trigger()
    dialog = window._child_windows["pair_overlap"]
    QtTest.QTest.qWait(200)
    ops = filter_ops()
    results["full_filter_boundary_checks"] = 0
    window.instances_dock.raise_()
    capture_index = 0

    def capture_widgets():
        """Record actual Qt rendering, composing host/dialog side by side."""
        global capture_index
        host, inspector = window.grab(), dialog.grab()
        canvas = QtGui.QPixmap(
            host.width() + inspector.width(), max(host.height(), inspector.height())
        )
        canvas.fill(QtCore.Qt.white)
        painter = QtGui.QPainter(canvas)
        painter.drawPixmap(0, 0, host)
        painter.drawPixmap(host.width(), 0, inspector)
        painter.end()
        canvas.save(str(output / f"record-{capture_index:04d}.png"))
        capture_index += 1

    capture_timer = QtCore.QTimer(dialog)
    capture_timer.timeout.connect(capture_widgets)
    capture_timer.start(100)
    for i, frame in enumerate(labels):
        window.state["frame_idx"] = i
        QtTest.QTest.qWait(500)
        for choice_index, instance_index in ((0, 0), (1, 1)):
            window.player.view.selectInstance(frame.instances[instance_index])
            button = next(
                b
                for b in dialog.findChildren(QtWidgets.QPushButton)
                if b.text() == f"Use canvas selection as {'AB'[choice_index]}"
            )
            QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        result = inspect_pair(*frame.instances[:2])
        assert "Unavailable" not in dialog.result.toPlainText()
        assert result["oks_ab"] == ops._compute_oks(
            *[x.numpy() for x in frame.instances[:2]]
        )
        # Verify that each displayed metric is the actual suppression boundary
        # in a complete native Labels-filter call. Keep source Labels untouched.
        for method, metric in (("iou", result["iou"]), ("oks", result["oks_ab"])):
            for threshold in (
                np.nextafter(metric, -np.inf),
                metric,
                np.nextafter(metric, np.inf),
            ):
                isolated = copy.deepcopy(sio.Labels([frame]))
                with np.errstate(invalid="ignore", divide="ignore"):
                    ops.filter_overlapping_instances(
                        isolated, threshold=threshold, method=method
                    )
                predicted = [
                    x
                    for x in isolated[0].instances
                    if isinstance(x, sio.PredictedInstance)
                ]
                assert len(predicted) == (1 if metric > threshold else 2)
                assert len(isolated[0].instances) == len(predicted) + 1
                results["full_filter_boundary_checks"] += 1
        if i == 1:
            assert result["oks_ab"] != result["oks_ba"]
        if i == 2:
            assert result["shared_nodes"] == 0
            assert "not evidence" in dialog.result.toPlainText()
        results["cases"].append(result)
        QtTest.QTest.qWait(1800)
        dialog.grab().save(str(output / f"inspector-{i}.png"))
        # Compose the real host and its real dialog into one recorded frame.
        window.grab().save(str(output / f"host-{i}.png"))
        host_image = Image.open(output / f"host-{i}.png").convert("RGB")
        rendered = Image.open(output / f"inspector-{i}.png").convert("RGB")
        composite = Image.new(
            "RGB",
            (
                host_image.width + rendered.width,
                max(host_image.height, rendered.height),
            ),
            "white",
        )
        composite.paste(host_image, (0, 0))
        composite.paste(rendered, (host_image.width, 0))
        composite.save(output / f"step-{i}.png")
    capture_timer.stop()
    results["captured_frames"] = capture_index
    # Same-instance and incompatible skeletons must not produce misleading scores.
    dialog.choices[1].setCurrentIndex(dialog.choices[0].currentIndex())
    assert "two different" in dialog.result.toPlainText()
    other = sio.Instance.from_numpy(a, sio.Skeleton(nodes=skeleton.node_names))
    try:
        inspect_pair(labels[0].instances[0], other)
        raise AssertionError("Incompatible skeleton was accepted")
    except ValueError as exc:
        assert "skeleton" in str(exc)
    # Degenerate boxes, all-missing coordinates and reordered node definitions.
    line = np.array([[45, 25 + n * 5] for n in range(6)], float)
    degenerate = [sio.Instance.from_numpy(p, skeleton) for p in (line, line + [0, 1])]
    assert all(inspect_pair(*degenerate)["degenerate"])
    empty = sio.Instance.from_numpy(
        np.full_like(a, np.nan), labels[0].instances[0].skeleton
    )
    assert inspect_pair(labels[0].instances[0], empty)["shared_nodes"] == 0
    reordered = sio.Instance.from_numpy(
        a, sio.Skeleton(nodes=skeleton.node_names[::-1])
    )
    try:
        inspect_pair(labels[0].instances[0], reordered)
        raise AssertionError("Reordered skeleton was accepted")
    except ValueError:
        pass
    # Manual source labels and stored prediction confidence stay distinct.
    dialog.choices[1].setCurrentIndex(2)
    assert "manual annotation" in dialog.choices[1].currentText()
    assert "not a prediction" in dialog.result.toPlainText()
    # No labeled frame: stale scores must disappear on navigation.
    window.state["labeled_frame"] = None
    dialog.refresh_frame()
    assert "at least two" in dialog.result.toPlainText()
    dialog.close()
    results["checks"] = [
        "embedded .slp loaded by actual MainWindow",
        "native Analyze action",
        "canvas selection buttons",
        "frame navigation",
        "directional OKS",
        "missing shared nodes",
        "same-instance rejection",
        "skeleton identity rejection",
        "reordered skeleton rejection",
        "zero-area and all-missing inputs",
        "manual confidence labeling",
        "empty-frame stale result clearing",
        "read-only model and source file",
    ]
assert before == snapshot(labels)
assert digest_before == hashlib.sha256(fixture.read_bytes()).hexdigest()
assert not window.state["has_changes"]
results["read_only"] = True
results["elapsed_seconds"] = round(time.perf_counter() - start, 3)
results["max_rss_bytes_macos"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
window.close()
qt.processEvents()

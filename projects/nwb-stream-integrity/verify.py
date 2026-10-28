"""Replay NWB Inspector #771 using constructed data and real HDF5/Zarr round trips."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
from hdmf.backends.hdf5 import H5DataIO
from hdmf.data_utils import DataChunkIterator, GenericDataChunkIterator
from hdmf_zarr import NWBZarrIO, ZarrDataIO
from nwbinspector import inspect_nwbfile_object
from nwbinspector.utils import _utils
from pynwb import NWBHDF5IO, NWBFile, TimeSeries


class ArrayChunks(GenericDataChunkIterator):
    """Small deterministic stand-in for a recording supplied in buffered chunks."""

    def __init__(self, data):
        self.array = data
        super().__init__(buffer_shape=(min(100, len(data)), 2), chunk_shape=(10, 2))

    def _get_dtype(self):
        return self.array.dtype

    def _get_maxshape(self):
        return self.array.shape

    def _get_data(self, selection):
        return self.array[selection]


def round_trip(directory, backend, iterator_type, rows, inspect_first):
    data = np.arange(1, rows * 2 + 1, dtype="int16").reshape(rows, 2)
    chunks = (
        DataChunkIterator(data, buffer_size=100)
        if iterator_type == "basic"
        else ArrayChunks(data)
    )
    wrapper, writer = (
        (H5DataIO, NWBHDF5IO) if backend == "hdf5" else (ZarrDataIO, NWBZarrIO)
    )
    nwb = NWBFile(
        session_description="Constructed stream-preservation experiment; no recorded neural data",
        identifier="constructed-stream",
        session_start_time=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    )
    nwb.add_acquisition(
        TimeSeries(name="signal", unit="a.u.", rate=100.0, data=wrapper(chunks))
    )
    messages = list(inspect_nwbfile_object(nwb)) if inspect_first else []
    path = directory / (
        "constructed.nwb" if backend == "hdf5" else "constructed.nwb.zarr"
    )
    with writer(str(path), "w") as io:
        io.write(nwb)
    with writer(str(path), "r") as io:
        written = io.read().acquisition["signal"].data[:]
    return {
        "backend": backend,
        "iterator": iterator_type,
        "rows": rows,
        "inspect_before_write": inspect_first,
        "rows_replaced_by_zeros": int((written == 0).all(axis=1).sum()),
        "values_equal": bool(np.array_equal(written, data)),
        "input_sha256": hashlib.sha256(data.tobytes()).hexdigest(),
        "output_sha256": hashlib.sha256(written.tobytes()).hexdigest(),
        "inspection_message_count": len(messages),
        "inspection_errors": [
            m.check_function_name for m in messages if m.importance.name == "ERROR"
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_file = Path(_utils.__file__).resolve()
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source_file.parents[3], text=True
    ).strip()
    expected_commit = "e6d968a1e0a62aa8f6611f45f242196d9ce75ea5"
    assert source_commit == expected_commit, (
        "Use the documented pinned upstream checkout"
    )
    started = time.monotonic()
    cases = []
    for backend in ["hdf5", "zarr"]:
        for iterator_type in ["basic", "generic"]:
            for rows in [50, 100, 500]:
                for inspect_first in [False, True]:
                    with tempfile.TemporaryDirectory(prefix="kufu-nwb-") as tmp:
                        cases.append(
                            round_trip(
                                Path(tmp), backend, iterator_type, rows, inspect_first
                            )
                        )
    controls = [c for c in cases if not c["inspect_before_write"]]
    inspected = [c for c in cases if c["inspect_before_write"]]
    assert all(c["values_equal"] for c in controls), (
        "Uninspected controls must preserve every value"
    )
    if args.expect == "patched":
        assert not any(c["inspection_errors"] for c in inspected), (
            "Inspector errors invalidate the patched replay"
        )
        assert all(c["values_equal"] for c in inspected), (
            "Inspection changed the saved values"
        )
    else:
        assert all(not c["values_equal"] for c in inspected), (
            "Baseline no longer reproduces; recheck the pin"
        )
    report = {
        "source": "https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771",
        "upstream_commit": source_commit,
        "shape_module_sha256": hashlib.sha256(source_file.read_bytes()).hexdigest(),
        "patch_sha256": hashlib.sha256(
            Path(__file__).with_name("non-consuming-shape.patch").read_bytes()
        ).hexdigest()
        if args.expect == "patched"
        else None,
        "expectation": args.expect,
        "input_kind": "Constructed positive int16 arrays, 2 channels at 100 Hz; not neural recordings",
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in [
                "nwbinspector",
                "pynwb",
                "hdmf",
                "hdmf-zarr",
                "h5py",
                "zarr",
                "numpy",
            ]
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "cases": cases,
        "controls_preserved": len(controls),
        "inspected_preserved": sum(c["values_equal"] for c in inspected),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()

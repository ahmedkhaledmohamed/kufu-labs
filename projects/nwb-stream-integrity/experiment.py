"""Parameterized, synthetic NWB round trips used by the execution lab."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

import numpy as np
from hdmf.backends.hdf5 import H5DataIO
from hdmf.data_utils import DataChunkIterator, GenericDataChunkIterator
from hdmf_zarr import NWBZarrIO, ZarrDataIO
from nwbinspector import inspect_nwbfile_object
from nwbinspector.utils import _utils
from pynwb import NWBHDF5IO, NWBFile, TimeSeries


def validate(config):
    required = {"rows", "channels", "buffer", "seed", "pattern", "backend", "iterator"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError("Unexpected experiment fields")
    for key, low, high in [
        ("rows", 1, 2000),
        ("channels", 1, 8),
        ("buffer", 1, 500),
        ("seed", 0, 2147483647),
    ]:
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError(f"Invalid {key}")
    for key, values in {
        "pattern": ["ramp", "random", "alternating"],
        "backend": ["hdf5", "zarr"],
        "iterator": ["basic", "generic"],
    }.items():
        if config[key] not in values:
            raise ValueError(f"Invalid {key}")
    return config


def generate(config):
    validate(config)
    shape = config["rows"], config["channels"]
    if config["pattern"] == "random":
        return np.random.Generator(np.random.PCG64(config["seed"])).integers(
            1, 30001, size=shape, dtype=np.int16
        )
    values = (np.arange(np.prod(shape), dtype=np.int32) % 30000 + 1).reshape(shape)
    if config["pattern"] == "alternating":
        values[1::2] *= -1
    return values.astype("int16")


class ArrayChunks(GenericDataChunkIterator):
    def __init__(self, data, buffer):
        self.array = data
        super().__init__(
            buffer_shape=(min(buffer, len(data)), data.shape[1]),
            chunk_shape=(1, data.shape[1]),
        )

    def _get_dtype(self):
        return self.array.dtype

    def _get_maxshape(self):
        return self.array.shape

    def _get_data(self, selection):
        return self.array[selection]


def round_trip(directory, config, inspected):
    expected = generate(config)
    chunks = (
        DataChunkIterator(expected.copy(), buffer_size=config["buffer"])
        if config["iterator"] == "basic"
        else ArrayChunks(expected.copy(), config["buffer"])
    )
    wrapper, writer = (
        (H5DataIO, NWBHDF5IO)
        if config["backend"] == "hdf5"
        else (ZarrDataIO, NWBZarrIO)
    )
    nwb = NWBFile(
        session_description="Synthetic software experiment; not a neural recording",
        identifier="kufu-synthetic",
        session_start_time=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    )
    nwb.add_acquisition(
        TimeSeries(name="signal", unit="a.u.", rate=100.0, data=wrapper(chunks))
    )
    messages = list(inspect_nwbfile_object(nwb)) if inspected else []
    output = directory / (
        "signal.nwb" if config["backend"] == "hdf5" else "signal.nwb.zarr"
    )
    with writer(str(output), "w") as io:
        io.write(nwb)
    with writer(str(output), "r") as io:
        actual = np.asarray(io.read().acquisition["signal"].data[:]).copy()
    shape_equal = actual.shape == expected.shape
    different = actual != expected if shape_equal else None
    positions = np.argwhere(different)[:8] if shape_equal else []
    errors = [m.check_function_name for m in messages if m.importance.name == "ERROR"]
    result = {
        "shape_equal": shape_equal,
        "dtype_equal": actual.dtype == expected.dtype,
        "values_equal": bool(np.array_equal(actual, expected)),
        "changed_values": int(different.sum()) if shape_equal else None,
        "changed_rows": int(different.any(axis=1).sum()) if shape_equal else None,
        "expected_shape": list(expected.shape),
        "actual_shape": list(actual.shape),
        "dtype": str(actual.dtype),
        "inspection_errors": errors,
        "input_sha256": hashlib.sha256(expected.tobytes()).hexdigest(),
        "output_sha256": hashlib.sha256(actual.tobytes()).hexdigest(),
        "examples": [
            {
                "row": int(r),
                "channel": int(c),
                "expected": int(expected[r, c]),
                "actual": int(actual[r, c]),
            }
            for r, c in positions
        ],
    }
    np.save(directory / "input.npy", expected, allow_pickle=False)
    np.save(directory / "output.npy", actual, allow_pickle=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["baseline", "patched"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    configs = json.loads(args.input.read_text())
    if not isinstance(configs, list) or not 1 <= len(configs) <= 4:
        raise ValueError("Supply 1–4 cases")
    cases = []
    for index, config in enumerate(configs):
        validate(config)
        case = {"input": config}
        # Every comparison has a fresh array, iterator, NWB object and file.
        for name, inspected in [("control", False), ("inspected", True)]:
            directory = args.output / str(index) / name
            directory.mkdir(parents=True)
            case[name] = round_trip(directory, config, inspected)
        cases.append(case)
    report = {
        "mode": args.mode,
        "python": platform.python_version(),
        "shape_module_sha256": hashlib.sha256(
            Path(_utils.__file__).read_bytes()
        ).hexdigest(),
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
        "cases": cases,
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {"mode": args.mode, "cases": len(cases), "python": sys.version.split()[0]}
        )
    )


if __name__ == "__main__":
    main()

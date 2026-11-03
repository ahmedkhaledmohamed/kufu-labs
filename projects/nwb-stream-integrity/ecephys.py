"""Convert constructed electrode samples through the installed Inspector and NWB writer."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import platform
import resource
import socket
import sys
import time
from pathlib import Path

import numpy as np
import nwbinspector
import pynwb
from hdmf.backends.hdf5 import H5DataIO
from hdmf.data_utils import GenericDataChunkIterator
from nwbinspector import inspect_nwbfile_object
from nwbinspector.utils import _utils
from pynwb.ecephys import ElectricalSeries

RATE = 20000.0
START = 0.25
CONVERSION = (
    1e-7  # Chosen fixture scale: 0.1 microvolt per ADC count, not device calibration.
)


def samples(start, stop, electrode_ids):
    """A deterministic integer pattern, including legitimate zeros; not brain activity."""
    times = np.arange(start, stop, dtype=np.int64)[:, None]
    ids = np.asarray(electrode_ids, dtype=np.int64)[None, :]
    return ((times * 17 + ids * 101) % 60001 - 30000).astype("<i2")


class GeneratedChunks(GenericDataChunkIterator):
    """Generate only the current buffer, retaining no full recording array."""

    def __init__(self, rows, ids, buffer):
        self.rows, self.ids = rows, np.asarray(ids)
        self.phase = "setup"
        self.reads = {phase: 0 for phase in ["setup", "inspection", "writing"]}
        self.first_rows = {}
        super().__init__(
            buffer_shape=(min(buffer, rows), len(ids)),
            chunk_shape=(min(1024, rows), len(ids)),
        )

    def _get_dtype(self):
        return np.dtype("<i2")

    def _get_maxshape(self):
        return self.rows, len(self.ids)

    def _get_data(self, selection):
        rows, columns = selection
        self.reads[self.phase] += 1
        self.first_rows.setdefault(self.phase, rows.start)
        return samples(rows.start, rows.stop, self.ids[columns])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--rows", type=int, default=16384)
    parser.add_argument("--channels", type=int, default=16)
    parser.add_argument("--buffer", type=int, default=4096)
    parser.add_argument("--skip-inspection", action="store_true")
    parser.add_argument(
        "--retain",
        action="store_true",
        help="Keep the constructed NWB file after verification",
    )
    parser.add_argument("--wheel-record", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert 1024 <= args.rows <= 4194304 and args.rows % 1024 == 0
    assert 2 <= args.channels <= 16
    assert 1024 <= args.buffer <= 16384 and args.buffer % 1024 == 0
    assert args.buffer <= args.rows
    assert platform.python_version() == "3.12.12"
    project = Path(__file__).resolve().parent
    profile = json.loads((project / "released-profile.json").read_text())
    version = f"0.7.2+kufu.{'baseline1' if args.expect == 'baseline' else 'stream1'}"
    assert nwbinspector.__version__ == version
    assert (
        Path(nwbinspector.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    ), "Use an installed wheel, not a source checkout"
    assert (
        hashlib.sha256(Path(_utils.__file__).read_bytes()).hexdigest()
        == profile[f"{args.expect}_shape_sha256"]
    )
    for name in ["pynwb", "hdmf"]:
        assert importlib.metadata.version(name) == profile["reported_stack"][name]
    installed = None
    if args.wheel_record:
        from verify_wheel import validate_installed

        installed = validate_installed(args.wheel_record, args.expect)

    # No recordings, streaming services or external data are used by this example.
    def offline(*args, **kwargs):
        raise OSError(
            "Network disabled during constructed electrophysiology conversion"
        )

    socket.create_connection = offline
    socket.socket.connect = offline
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    order = list(reversed(range(args.channels)))
    ids = [1000 + index for index in order]
    scales = np.linspace(1.0, 1.15, args.channels)
    expected_scales = scales.copy()
    nwb = pynwb.NWBFile(
        session_description="Constructed electrode stream for software verification; no neural recording",
        identifier=f"constructed-ecephys-{args.rows}-{args.channels}",
        session_start_time=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    )
    device_model = nwb.create_device_model(
        name="fixture_model", manufacturer="Constructed software fixture"
    )
    device = nwb.create_device(name="fixture_device", model=device_model)
    group = nwb.create_electrode_group(
        name="fixture_group",
        description="Constructed metadata; not a physical probe",
        location="not_applicable",
        device=device,
    )
    nwb.add_electrode_column(
        name="label", description="Constructed electrode identifier"
    )
    for index in range(args.channels):
        nwb.add_electrode(
            id=1000 + index,
            group=group,
            location="not_applicable",
            label=f"fixture electrode {index}",
        )
    electrodes = nwb.create_electrode_table_region(
        region=order,
        description="Data columns reference electrode table rows in reversed order",
    )
    stream = GeneratedChunks(args.rows, ids, args.buffer)
    series = ElectricalSeries(
        name="constructed_voltage",
        data=H5DataIO(stream, chunks=(1024, args.channels)),
        electrodes=electrodes,
        conversion=CONVERSION,
        channel_conversion=scales,
        starting_time=START,
        rate=RATE,
        description="Deterministic ADC-count pattern, not neural activity or a biological simulation",
    )
    nwb.add_acquisition(series)
    stream.phase = "inspection"
    messages = [] if args.skip_inspection else list(inspect_nwbfile_object(nwb))
    stream.phase = "writing"
    file = args.output / "constructed_ecephys.nwb"
    with pynwb.NWBHDF5IO(file, "w") as io:
        io.write(nwb)
    file_bytes = file.stat().st_size
    assert file_bytes < 160 * 1024 * 1024
    expected_hash, actual_hash = hashlib.sha256(), hashlib.sha256()
    changed_rows = changed_values = legitimate_zero_values = 0
    with pynwb.NWBHDF5IO(file, "r") as io:
        reopened = io.read()
        saved = reopened.acquisition["constructed_voltage"]
        assert saved.data.shape == (args.rows, args.channels)
        assert saved.data.dtype == np.dtype("<i2")
        assert (
            saved.unit == "volts"
            and saved.conversion == CONVERSION
            and saved.offset == 0.0
        )
        assert (
            saved.starting_time == START
            and saved.rate == RATE
            and saved.timestamps is None
        )
        assert np.array_equal(saved.channel_conversion[:], expected_scales)
        assert np.array_equal(scales, expected_scales)
        assert list(saved.electrodes.data[:]) == order
        table_ids = list(saved.electrodes.table.id[:])
        column_ids = [int(table_ids[index]) for index in order]
        assert column_ids == ids
        labels = list(saved.electrodes.table["label"].data[:])
        assert [labels[index] for index in order] == [
            f"fixture electrode {index}" for index in order
        ]
        assert reopened.session_start_time == nwb.session_start_time
        example = {
            "expected_counts": samples(0, 1, ids)[0, :4].tolist(),
            "saved_counts": saved.data[0, :4].tolist(),
        }
        for offset in range(0, args.rows, args.buffer):
            stop = min(offset + args.buffer, args.rows)
            expected = samples(offset, stop, ids)
            actual = saved.data[offset:stop, :]
            assert actual.shape == expected.shape and actual.dtype == expected.dtype
            different = actual != expected
            changed_rows += int(np.any(different, axis=1).sum())
            changed_values += int(np.count_nonzero(different))
            legitimate_zero_values += int(np.count_nonzero(expected == 0))
            expected_hash.update(expected.tobytes())
            actual_hash.update(actual.tobytes())
        # Format validity and source-data preservation are distinct checks.
        validation_errors = pynwb.validate(io=io)
        assert not validation_errors, str(validation_errors)
    errors = [m.check_function_name for m in messages if m.importance.name == "ERROR"]
    preserved = changed_values == 0
    if args.skip_inspection or args.expect == "patched":
        assert preserved, "The installed repair/control changed the generated stream"
        assert stream.reads["inspection"] == 0
    else:
        assert not preserved and stream.reads["inspection"] > 0, (
            "Expected baseline stream consumption"
        )
    if args.expect == "patched":
        assert not errors, f"Patched inspection has errors: {errors}"
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    assert peak_rss < 512 * 1024 * 1024
    report = {
        "example_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "expectation": args.expect,
        "installed_version": version,
        "installed_build": installed,
        "input_kind": "Constructed signed ADC counts including valid zeros; not a recording or biological simulation",
        "input": {
            "rows": args.rows,
            "channels": args.channels,
            "buffer_rows": args.buffer,
        },
        "inspected": not args.skip_inspection,
        "values_preserved": preserved,
        "changed_rows": changed_rows,
        "changed_values": changed_values,
        "legitimate_zero_values": legitimate_zero_values,
        "expected_sha256": expected_hash.hexdigest(),
        "saved_sha256": actual_hash.hexdigest(),
        "metadata": {
            "column_electrode_ids": ids,
            "unit": "volts",
            "conversion_volts_per_count": CONVERSION,
            "channel_conversion": scales.tolist(),
            "starting_time_seconds": START,
            "rate_hz": RATE,
            "last_sample_time_seconds": START + (args.rows - 1) / RATE,
            "preserved": True,
        },
        "first_sample_example": example,
        "iterator_buffers_requested": stream.reads,
        "first_requested_row": stream.first_rows,
        "inspection_errors": errors,
        "inspection_message_count": len(messages),
        "schema_validation_errors": len(validation_errors),
        "array_bytes": args.rows * args.channels * 2,
        "file_bytes": file_bytes,
        "peak_rss_bytes": peak_rss,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "file_retained": args.retain,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["pynwb", "hdmf", "numpy", "h5py"]
        },
    }
    if not args.retain:
        file.unlink()
    (args.output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()

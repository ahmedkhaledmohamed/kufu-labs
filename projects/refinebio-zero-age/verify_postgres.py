"""Run the model replay in a disposable private-socket PostgreSQL cluster."""

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgres-bin", type=Path, required=True)
    parser.add_argument("--clean-checkout", type=Path, required=True)
    parser.add_argument("--patched-checkout", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    binaries = args.postgres_bin.resolve()
    for name in ["postgres", "initdb", "pg_ctl", "createdb"]:
        assert (binaries / name).is_file(), name
    version = subprocess.check_output(
        [str(binaries / "postgres"), "--version"], text=True
    ).strip()
    env = {key: value for key, value in os.environ.items() if not key.startswith("PG")}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kufu-age-pg-") as tmp:
        root = Path(tmp)
        password_file, service_file = root / "pgpass", root / "pg_service.conf"
        password_file.write_text("")
        password_file.chmod(0o600)
        service_file.write_text("")
        env.update(PGPASSFILE=str(password_file), PGSERVICEFILE=str(service_file))
        data, sockets = root / "data", root / "sockets"
        sockets.mkdir(mode=0o700)
        subprocess.run(
            [
                str(binaries / "initdb"),
                "-D",
                str(data),
                "--username=kufu_fixture",
                "--auth-local=trust",
                "--auth-host=reject",
                "--encoding=UTF8",
                "--locale=C",
            ],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        try:
            subprocess.run(
                [
                    str(binaries / "pg_ctl"),
                    "-D",
                    str(data),
                    "-l",
                    str(root / "postgres.log"),
                    "-o",
                    f"-k {shlex.quote(str(sockets))} -p 55387 -c listen_addresses=''",
                    "-w",
                    "start",
                ],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            for mode, checkout in [
                ("baseline", args.clean_checkout),
                ("patched", args.patched_checkout),
            ]:
                subprocess.run(
                    [
                        str(binaries / "createdb"),
                        "-h",
                        str(sockets),
                        "-p",
                        "55387",
                        "-U",
                        "kufu_fixture",
                        mode,
                    ],
                    env=env,
                    check=True,
                )
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).with_name("verify_export.py")),
                        "--checkout",
                        str(checkout),
                        "--expect",
                        mode,
                        "--output",
                        str(args.output_dir / f"postgres-{mode}.json"),
                        "--postgres-socket",
                        str(sockets),
                        "--postgres-name",
                        mode,
                    ],
                    env=env,
                    check=True,
                )
        finally:
            if (data / "postmaster.pid").exists():
                subprocess.run(
                    [
                        str(binaries / "pg_ctl"),
                        "-D",
                        str(data),
                        "-m",
                        "fast",
                        "-w",
                        "stop",
                    ],
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                )
    print(
        json.dumps({"postgres": version, "private_cluster_stopped_and_removed": True})
    )


if __name__ == "__main__":
    main()

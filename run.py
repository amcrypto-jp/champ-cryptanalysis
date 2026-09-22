#!/usr/bin/env python3
"""Run the CHAMP review evidence. Quick mode requires only Python >=3.8.

--full uses the 40-bit MITM demonstration and regenerates all 12 toy collisions.
--submission-root additionally checks all four original C builds and selected KATs.
--sage additionally performs proof-enabled parameter checks with SageMath.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def main():
    if not __debug__ or os.environ.get("PYTHONOPTIMIZE"):
        raise SystemExit("Assertions are required; disable -O and PYTHONOPTIMIZE")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--submission-root", type=Path)
    parser.add_argument("--cc", default="gcc", help="C compiler executable")
    parser.add_argument("--sage", help="SageMath executable, e.g. sage")
    parser.add_argument("--output-dir", type=Path, default=Path("verification-output"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    def execute(label, command):
        print(f"\nRunning {label}", flush=True)
        with (args.output_dir / f"{label}.log").open("w") as log:
            result = subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, env=env)
            for line in result.stdout:
                print(line, end="", flush=True)
                log.write(line)
            rc = result.wait()
        if rc:
            raise SystemExit(f"FAILED: {label} (exit {rc})")

    execute("certificates", [sys.executable, str(PACKAGE / "code/check_collisions.py")])
    command = [sys.executable, "-u", str(PACKAGE / "code/reproduce.py"),
               "--mitm-bits", "40" if args.full else "24"]
    if args.submission_root:
        command += ["--submission-root", str(args.submission_root.resolve()), "--cc", args.cc]
    execute("reproduce-full" if args.full else "reproduce-quick", command)
    if args.full:
        generated = args.output_dir / "regenerated-collisions.json"
        execute("subgroup", [sys.executable, "-u", str(PACKAGE / "code/subgroup.py"),
                             "--output", str(generated)])
        execute("regenerated-certificates", [sys.executable,
                str(PACKAGE / "code/check_collisions.py"), str(generated)])
        saved = json.loads((PACKAGE / "data/collisions.json").read_text())
        replay = json.loads(generated.read_text())
        # Wall-clock timing is deliberately excluded from deterministic replay.
        stable = lambda rows: [{k: v for k, v in row.items() if k != "seconds"}
                               for row in rows]
        if stable(saved) != stable(replay):
            raise SystemExit("FAILED: seeded collision replay differs from saved certificates")
        (args.output_dir / "replay.log").write_text(
            "PASS: all 12 seeded collision records reproduce exactly, excluding timings.\n")
        print("PASS: all 12 seeded collision records reproduce exactly, excluding timings.")
    if args.sage:
        # Sage preparses .sage files; isolate its generated files in a temporary directory.
        with tempfile.TemporaryDirectory(prefix="champ-parameter-proof-") as tmp:
            script = Path(tmp) / "parameters.sage"
            script.write_text((PACKAGE / "code/parameters.sage").read_text())
            execute("parameters", [args.sage, str(script)])
    print("\nPASS: all requested checks completed.")
    if not args.submission_root:
        print("Original C implementations and KATs were not requested.")
    if not args.sage:
        print("Proof-enabled primality checks were not requested.")


if __name__ == "__main__":
    main()

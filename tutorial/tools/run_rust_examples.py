"""Run the five real Rust API examples with the paper's nightly toolchain.

Usage: python3 tutorial/tools/run_rust_examples.py [all|01_mle|...] [--offline]
Full logs and a JSON report are saved to .build/results/.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ["01_mle", "02_sumcheck", "03_einsum", "04_pcs", "05_dag_pcs"]
TOOLCHAIN = "nightly-2025-07-01"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", nargs="?", default="all", choices=["all", *EXAMPLES])
    parser.add_argument("--offline", action="store_true", help="require already cached dependencies")
    args = parser.parse_args()
    env = os.environ.copy()
    for key, path in [("CARGO_HOME", ".build/cargo"), ("RUSTUP_HOME", ".build/rustup"),
                      ("CARGO_TARGET_DIR", ".build/target")]:
        env.setdefault(key, str(ROOT / path))
    env.setdefault("CARGO_BUILD_JOBS", "2")
    output = ROOT / ".build/results"
    output.mkdir(parents=True, exist_ok=True)
    version = subprocess.check_output(
        ["rustup", "run", TOOLCHAIN, "rustc", "--version"], cwd=ROOT, env=env, text=True).strip()
    report = {
        "toolchain": TOOLCHAIN, "rustc": version,
        "cpu_manifest": "tutorial/cpu/Cargo.toml",
        "lock_sha256": hashlib.sha256((ROOT / "tutorial/project/Cargo.lock").read_bytes()).hexdigest(),
        "examples": [],
    }
    selected = EXAMPLES if args.example == "all" else [args.example]
    for name in selected:
        command = ["cargo", "+" + TOOLCHAIN, "run", "--manifest-path",
                   "tutorial/project/Cargo.toml", "--example", name, "--locked"]
        if args.offline:
            command.append("--offline")
        command += ["--", "upstream/config.yaml"]
        log_path = output / f"{name}.log"
        print("Running", name, "with", version, flush=True)
        with log_path.open("w") as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        report["examples"].append({"name": name, "exit_code": result.returncode,
                                   "log": str(log_path.relative_to(ROOT)), "command": command})
        (output / "rust-report.json").write_text(json.dumps(report, indent=2) + "\n")
        if result.returncode:
            print("\n".join(log_path.read_text().splitlines()[-50:]))
            return result.returncode
        print("  PASS; log:", log_path.relative_to(ROOT), flush=True)
    print("All selected Rust examples passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

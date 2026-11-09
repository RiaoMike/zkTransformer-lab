"""验证课程材料。不会填充作业，也不会下载或构建整个原库。"""
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*command):
    print("+", " ".join(str(c) for c in command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    manifest = json.loads((ROOT / "tutorial/reference/upstream_manifest.json").read_text())
    for entry in manifest["files"]:
        data = (ROOT / "upstream" / entry["path"]).read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if sha != entry["git_blob_sha1"]:
            raise ValueError("上游快照已变更：" + entry["path"])
    print(f"{len(manifest['files'])} upstream Git blob hashes matched", flush=True)

    original = tomllib.loads((ROOT / "upstream/Cargo.toml").read_text())
    cpu = tomllib.loads((ROOT / "tutorial/cpu/Cargo.toml").read_text())
    assert cpu["features"]["default"] == original["features"]["default"]
    assert set(cpu["dependencies"]) == set(original["dependencies"])
    for name, dependency in original["dependencies"].items():
        expected = dependency
        if name.startswith("icicle-"):
            expected = {**dependency, "optional": True}
        elif name == "tract-onnx":
            expected = {"version": dependency, "optional": True}
        assert cpu["dependencies"][name] == expected, name
    print("CPU manifest matches upstream dependencies with explicit optional gates", flush=True)

    import source
    for key in source.ENTRIES:
        source.locate(key)
    for path in [ROOT / "README.md", *(ROOT / "tutorial").rglob("*.md")]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            local = target.split("#")[0]
            if not (path.parent / local).exists():
                raise ValueError(f"失效本地链接 {path}: {target}")
    print("source anchors and local Markdown links passed", flush=True)
    run(sys.executable, "tutorial/check_exercises.py", "all", "--reference")
    run(sys.executable, "tutorial/labs.py", "all")
    run(sys.executable, "tutorial/tools/trace_claims.py")
    print("Teaching materials passed; run tutorial/tools/run_rust_examples.py for Rust API checks.")


if __name__ == "__main__":
    main()

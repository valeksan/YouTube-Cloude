#!/usr/bin/env python3
"""Collect installed Python notices without claiming a complete binary SBOM.

Run in an isolated build environment. Native libraries and APK target packages
need separate review; see docs/LICENSING_AUDIT.md.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import sys
import sysconfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def is_notice(path: PurePosixPath) -> bool:
    parts = [part.lower() for part in path.parts]
    return (
        any(part in {"licenses", "licences"} for part in parts[:-1])
        or bool(re.match(r"^(licen[cs]e|copying|notice|copyright|authors)([._-]|$)", parts[-1]))
        or parts[-1].endswith((".license", ".licence"))
    )


def collect(output: Path, required: list[str]) -> dict:
    """Write notices and exact installed versions; reject missing required notices."""
    if output.exists():
        raise ValueError(f"Output already exists: {output}; choose a fresh directory")
    required_names = {canonical_name(name) for name in required}
    distributions = sorted(
        metadata.distributions(),
        key=lambda dist: (canonical_name(dist.metadata["Name"]), dist.version),
    )
    inventory = []
    found = set()
    for dist in distributions:
        name = dist.metadata["Name"]
        key = canonical_name(name)
        # Editable installs may expose both source egg-info and wheel dist-info.
        # Project notices are copied from the checkout below, not from either.
        if key == "youtube-cloude":
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:[-a-z0-9]*[a-z0-9])?", key):
            raise ValueError(f"Invalid distribution name: {name}")
        if key in found:
            raise ValueError(f"Duplicate installed distribution: {name}")
        found.add(key)
        version_dir = re.sub(r"[^a-zA-Z0-9._+-]", "_", dist.version)
        copied = []
        missing = []
        for file in sorted(dist.files or [], key=str):
            relative = PurePosixPath(str(file).replace("\\", "/"))
            if not is_notice(relative):
                continue
            if relative.is_absolute() or ".." in relative.parts or ":" in str(relative):
                raise ValueError(f"Unsafe notice path in {name}: {file}")
            source = Path(dist.locate_file(file))
            if not source.is_file():
                missing.append(str(relative))
                continue
            target = output / "packages" / key / version_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            target.write_bytes(data)
            copied.append({
                "path": target.relative_to(output).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        inventory.append({
            "name": name,
            "version": dist.version,
            "declared_license": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
            "notice_files": copied,
            "missing_notice_files": missing,
        })

    output.mkdir(parents=True, exist_ok=True)
    for relative in ["LICENSE", "THIRD_PARTY_NOTICES.md", "CONTRIBUTORS.md",
                     "recipes/LICENSE", "docs/LICENSING_AUDIT.md"]:
        target = output / "project" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT_ROOT / relative, target)

    runtime_notice = None
    for source in [Path(sysconfig.get_path("stdlib")) / "LICENSE.txt",
                   Path(sys.base_prefix) / "LICENSE.txt"]:
        if source.is_file():
            data = source.read_bytes()
            target = output / "python-runtime-LICENSE.txt"
            target.write_bytes(data)
            runtime_notice = {"path": target.name, "sha256": hashlib.sha256(data).hexdigest()}
            break

    report = {
        "scope": "Installed Python build environment; not a complete final-artifact SBOM or licensing clearance",
        "python": platform.python_version(),
        "platform": platform.system(),
        "python_runtime_notice": runtime_notice,
        "packages": inventory,
    }
    (output / "build-environment.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    unresolved = required_names - found
    unresolved.update(
        canonical_name(item["name"]) for item in inventory
        if canonical_name(item["name"]) in required_names
        and (not item["notice_files"] or item["missing_notice_files"])
    )
    if unresolved:
        raise ValueError("Missing package or incomplete notice files: " + ", ".join(sorted(unresolved)))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require", nargs="+", default=[])
    args = parser.parse_args()
    try:
        report = collect(args.output, args.require)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"License collection failed: {exc}\n")
    print(f"Collected notices for {len(report['packages'])} installed distributions into {args.output}")


if __name__ == "__main__":
    main()

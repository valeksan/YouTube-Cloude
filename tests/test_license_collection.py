"""Release notice completeness and unsafe-path failure cases."""
from email.message import Message
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "collect_licenses", Path(__file__).resolve().parents[1] / "scripts/collect_licenses.py"
)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class Distribution:
    def __init__(self, root, files, name="Example_Package"):
        self.metadata = Message()
        self.metadata["Name"] = name
        self.metadata["License-Expression"] = "BSD-3-Clause"
        self.version = "1.2.3"
        self.files = files
        self.root = root

    def locate_file(self, path):
        return self.root / path


def test_preserves_nested_notices_and_versions(tmp_path, monkeypatch):
    paths = ["example.dist-info/licenses/LICENSE", "example/native/licenses/LGPL.txt", "example/NOTICE"]
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"original copyright and permission\r\n")
    dist = Distribution(tmp_path, paths + ["example/code.py"])
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [dist])
    output = tmp_path / "legal"
    report = collector.collect(output, ["example-package"])
    entry = report["packages"][0]
    assert entry["version"] == "1.2.3"
    assert len(entry["notice_files"]) == 3
    for notice in entry["notice_files"]:
        data = (output / notice["path"]).read_bytes()
        assert data == b"original copyright and permission\r\n"
        assert hashlib.sha256(data).hexdigest() == notice["sha256"]
    assert json.loads((output / "build-environment.json").read_text()) == report
    assert (output / "project/recipes/LICENSE").is_file()
    assert (output / "project/docs/QT_RELEASE_REVIEW.md").is_file()


@pytest.mark.parametrize("files", [[], ["example.dist-info/LICENSE"]])
def test_declared_license_does_not_replace_missing_text(tmp_path, monkeypatch, files):
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [Distribution(tmp_path, files)])
    with pytest.raises(ValueError, match="incomplete notice"):
        collector.collect(tmp_path / "legal", ["example-package"])


def test_required_package_must_be_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [])
    with pytest.raises(ValueError, match="missing-dependency"):
        collector.collect(tmp_path / "legal", ["missing-dependency"])


@pytest.mark.parametrize("name", ["PySide6-Essentials", "PySide6-Addons", "shiboken6"])
def test_qt_commercial_reference_is_not_open_source_notice(tmp_path, monkeypatch, name):
    relative = "package.dist-info/licenses/LicenseRef-Qt-Commercial.txt"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("Commercial license reference")
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [Distribution(tmp_path, [relative], name)])
    with pytest.raises(ValueError, match="incomplete notice"):
        collector.collect(tmp_path / "legal", [name])
    assert (tmp_path / "legal/build-environment.json").is_file()


def test_qt_required_open_source_texts_are_collected(tmp_path, monkeypatch):
    paths = ["package.dist-info/licenses/LGPL-3.0-only.txt", "package.dist-info/licenses/GPL-3.0-only.txt"]
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test fixture, not a license clearance")
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [Distribution(tmp_path, paths, "shiboken6")])
    assert len(collector.collect(tmp_path / "legal", ["shiboken6"])["packages"][0]["notice_files"]) == 2


def test_editable_project_metadata_does_not_duplicate_project_notices(tmp_path, monkeypatch):
    editable = Distribution(tmp_path, [], name="youtube-cloude")
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [editable, editable])
    output = tmp_path / "legal"
    report = collector.collect(output, [])
    assert report["packages"] == []
    assert (output / "project/LICENSE").is_file()


def test_rejects_parent_traversal_in_record(tmp_path, monkeypatch):
    dist = Distribution(tmp_path, ["../../../LICENSE"])
    monkeypatch.setattr(collector.metadata, "distributions", lambda: [dist])
    with pytest.raises(ValueError, match="Unsafe notice path"):
        collector.collect(tmp_path / "legal", [])


def test_does_not_overwrite_existing_output(tmp_path):
    marker = tmp_path / "keep.txt"
    marker.write_text("keep")
    with pytest.raises(ValueError, match="already exists"):
        collector.collect(tmp_path, [])
    assert marker.read_text() == "keep"

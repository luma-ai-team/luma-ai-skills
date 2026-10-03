import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from package_openai import PLUGIN, build


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plugin = self.root / "plugin"
        shutil.copytree(PLUGIN, self.plugin)

    def tearDown(self):
        self.temp.cleanup()

    def test_reproducible_root_package_without_private_files(self):
        (self.plugin / ".env").write_text("SHOULD_NOT_SHIP=fixture")
        first, second = self.root / "first.zip", self.root / "second.zip"
        build(self.plugin, first)
        build(self.plugin, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            names = archive.namelist()
            self.assertIn("plugin.json", names)
            self.assertIn("mcp.json", names)
            self.assertIn("skills/_shared/luma-tools.md", names)
            self.assertEqual(len([name for name in names if name.endswith("/SKILL.md")]), 10)
            self.assertFalse(any(name.startswith(".") or "/." in name for name in names))

    def test_credentials_in_manifest_are_rejected(self):
        path = self.plugin / "plugin.json"
        data = json.loads(path.read_text())
        data["extensions"]["com.openai"]["review"]["test_credentials"] = "fixture"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Private review"):
            build(self.plugin, self.root / "bad.zip")

    def test_skill_symlink_is_rejected(self):
        (self.plugin / "skills" / "leak.md").symlink_to(self.root / "outside.md")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            build(self.plugin, self.root / "bad.zip")

    def test_unexpected_skill_file_is_rejected(self):
        (self.plugin / "skills" / ".env").write_text("fixture")
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            build(self.plugin, self.root / "bad.zip")

    def test_static_authorization_header_is_rejected(self):
        path = self.plugin / "mcp.json"
        data = json.loads(path.read_text())
        data["mcpServers"]["luma-ai"]["headers"] = {"Authorization": "fixture"}
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "OAuth-only"):
            build(self.plugin, self.root / "bad.zip")

    def test_hooks_and_app_manifest_are_rejected(self):
        for name in ["hooks", ".app.json"]:
            path = self.plugin / name
            path.mkdir() if name == "hooks" else path.write_text("{}")
            with self.assertRaisesRegex(ValueError, "Public packages"):
                build(self.plugin, self.root / "bad.zip")
            path.rmdir() if name == "hooks" else path.unlink()


if __name__ == "__main__":
    unittest.main()

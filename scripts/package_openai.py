"""Build the public OpenAI ZIP from an explicit, credential-free file set."""

import argparse
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/luma"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(plugin):
    manifest = json.loads((plugin / "plugin.json").read_text())
    mcp = json.loads((plugin / "mcp.json").read_text())
    require(manifest.get("name") == "luma", "Expected the Luma plugin")
    require(re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")), "Invalid version")
    require(manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "Invalid manifest schema")
    require(mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "Invalid MCP schema")
    require(mcp.get("mcpServers") == {"luma-ai": {"type": "streamable-http", "url": "https://luma.ai/api/mcp"}}, "Expected OAuth-only production MCP configuration")
    extension = manifest["extensions"]["com.openai"]
    interface = extension["interface"]
    for key, limit in [("displayName", 30), ("shortDescription", 30), ("longDescription", 4000), ("developerName", 80)]:
        value = interface.get(key)
        require(isinstance(value, str) and 0 < len(value) <= limit, "Invalid listing field: " + key)
    for key in ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]:
        value = interface.get(key, "")
        require(value.startswith("https://") and "@" not in value and len(value) <= 1024, "Invalid public URL: " + key)
    for key in ["composerIcon", "logo"]:
        name = interface[key]
        require(name.startswith("./assets/") and ".." not in name, "Invalid icon path")
        asset = plugin / name
        require(asset.is_file() and asset.stat().st_size <= 5 * 1024 * 1024, "Missing or oversized icon")
        svg = ET.parse(asset).getroot()
        width, height = float(svg.attrib["width"]), float(svg.attrib["height"])
        require(width == height and width >= 48, "Icon must be square and at least 48px")
    cases = extension["review"]["test_cases"]
    for kind, count in [("positive", 5), ("negative", 3)]:
        require(len(cases[kind]) == count, "Incorrect review case count")
        for case in cases[kind]:
            for key in ["description", "prompt", "expected_behavior"] + (["tools_triggered"] if kind == "positive" else []):
                require(isinstance(case.get(key), str) and case[key], "Incomplete review case")
    serialized = json.dumps(manifest).lower()
    require("test_credentials" not in serialized and "reviewer_instructions" not in serialized, "Private review fields are prohibited")
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    require(len(skills) == 10, "Expected ten canonical workflows")
    return manifest


def package_files(plugin):
    require(not (plugin / ".app.json").exists(), "Public packages cannot contain an app manifest")
    require(not (plugin / "hooks").exists(), "Public packages cannot contain hooks")
    files = [plugin / name for name in ["plugin.json", "mcp.json", "LICENSE"]]
    for directory, suffix in [("assets", ".svg"), ("skills", ".md")]:
        base = plugin / directory
        for path in sorted(base.rglob("*")):
            require(not path.is_symlink(), "Symlinks are prohibited: " + str(path))
            if path.is_file():
                require(path.suffix == suffix and not any(part.startswith(".") for part in path.relative_to(base).parts), "Unexpected packaged file: " + str(path))
                files.append(path)
    for path in files:
        require(path.is_file() and not path.is_symlink(), "Missing file or symlink: " + str(path))
        require(path.resolve().is_relative_to(plugin.resolve()), "File escapes the plugin")
    return sorted(files)


def build(plugin, output):
    manifest = validate(plugin)
    files = package_files(plugin)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(plugin).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return manifest, len(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = validate(PLUGIN)
    output = args.output or ROOT / "dist" / ("luma-openai-" + manifest["version"] + ".zip")
    manifest, count = build(PLUGIN, output)
    print(f"Built {output}: {count} files, version {manifest['version']}. Review cases are plans, not executed evidence.")

"""Check reviewed public hosts, package/image registries and private-key material.

This is a portability guard, not a replacement for a dedicated secret scanner.
Adding a provider requires reviewing and extending the allowlist explicitly.
"""
import os
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
skip = {".git", ".venv", "node_modules", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "artifacts", "test-results", "playwright-report"}
public_hosts = {
    "docs.astral.sh", "docs.djangoproject.com", "eslint.org", "files.pythonhosted.org",
    "github.com", "opencollective.com", "pypi.org", "react.dev", "registry.npmjs.org",
    "tidelift.com",
}
local_test_hosts = {"localhost", "127.0.0.1", "api", "attacker.invalid"}
image_registries = {"docker.io", "ghcr.io"}
findings = []
for directory, folders, names in os.walk(root):
    folders[:] = [name for name in folders if name not in skip]
    for name in names:
        path = Path(directory) / name
        if name.startswith(".env") and name != ".env.example":
            continue
        if path.suffix in {".png", ".zip", ".pyc", ".tsbuildinfo"} or name == ".coverage":
            continue
        text = path.read_text(errors="replace")
        hosts = set(re.findall(r"https?://([A-Za-z0-9.-]+)", text))
        if hosts - public_hosts - local_test_hosts:
            findings.append(str(path.relative_to(root)))
        for image in re.findall(r"(?:FROM|--from=|image:)\s*([^\s]+)", text):
            registry = image.split("/")[0]
            if "/" in image and "." in registry and registry not in image_registries:
                findings.append(str(path.relative_to(root)))
        if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", text):
            findings.append(str(path.relative_to(root)))
if findings:
    raise SystemExit("Unreviewed host/registry or key material: " + ", ".join(sorted(set(findings))))
print("Portability scan passed")

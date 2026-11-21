"""Check generated files without modifying the working tree; works before git init too."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temporary:
    schema = Path(temporary) / "openapi.json"
    types = Path(temporary) / "schema.d.ts"
    subprocess.run([os.environ.get("UV", "uv"), "run", "--directory", str(root / "backend"),
                    "--frozen", "python", "manage.py", "export_contract", str(schema),
                    "--settings=config.test_settings"], check=True)
    subprocess.run([str(root / "frontend/node_modules/.bin/openapi-typescript"), str(schema),
                    "-o", str(types)], check=True, cwd=root)
    for generated, tracked in [(schema, root / "contracts/openapi.json"),
                               (types, root / "frontend/src/shared/api/schema.d.ts")]:
        if generated.read_bytes() != tracked.read_bytes():
            raise SystemExit(f"Contract drift in {tracked.relative_to(root)}; run make contract")
print("Contract and TypeScript types match")

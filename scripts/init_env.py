"""Create local-only configuration once. Existing secrets are never overwritten."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    raise SystemExit(".env already exists; kept unchanged")
content = (root / ".env.example").read_text()
content = content.replace("DJANGO_SECRET_KEY=\n", "DJANGO_SECRET_KEY=" + secrets.token_urlsafe(64) + "\n")
content = content.replace("POSTGRES_PASSWORD=\n", "POSTGRES_PASSWORD=" + secrets.token_urlsafe(32) + "\n")
with path.open("x") as stream:
    stream.write(content)
path.chmod(0o600)
print("Created .env for local development; secrets are not printed")

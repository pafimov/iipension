import json
from pathlib import Path

from django.core.management.base import BaseCommand

from pension.api import api


class Command(BaseCommand):
    help = "Write the deterministic OpenAPI contract; generated types must match it"

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        schema = api.get_openapi_schema(path_prefix="/api/v1/")
        Path(options["path"]).write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")

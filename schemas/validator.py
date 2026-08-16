import json
from pathlib import Path

import jsonschema

SCHEMAS_DIR = Path(__file__).parent


def assert_matches_schema(instance, schema_name):
    schema_path = SCHEMAS_DIR / f"{schema_name}.json"
    with open(schema_path) as f:
        schema = json.load(f)

    jsonschema.validate(instance=instance, schema=schema)

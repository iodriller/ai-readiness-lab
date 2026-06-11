"""Export the domain models as a single JSON Schema bundle.

The frontend converts the emitted `backend/schema.json` into TypeScript types
(`frontend/src/api/types.ts`) so both sides share one contract.

Usage:
    python -m app.models.export        # writes backend/schema.json
"""

import json
from pathlib import Path

from pydantic.json_schema import models_json_schema

from app.models import TOP_LEVEL_MODELS

_OUTPUT = Path(__file__).resolve().parents[2] / "schema.json"


def build_schema() -> dict:
    _, bundle = models_json_schema(
        [(model, "validation") for model in TOP_LEVEL_MODELS],
        title="AIReadinessLabModels",
    )
    # Reference each top-level model from the root so the TypeScript generator
    # emits a named interface for every one (json2ts skips unreferenced $defs).
    bundle["type"] = "object"
    bundle["properties"] = {
        model.__name__: {"$ref": f"#/$defs/{model.__name__}"} for model in TOP_LEVEL_MODELS
    }
    return bundle


def main() -> None:
    _OUTPUT.write_text(json.dumps(build_schema(), indent=2) + "\n")
    print(f"Wrote {_OUTPUT}")


if __name__ == "__main__":
    main()

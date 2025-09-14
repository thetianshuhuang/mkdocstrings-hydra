# Generate a JSON schema of the Hydra handler configuration.

import json
from dataclasses import dataclass, fields
from os.path import join
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from mkdocstrings_handlers.hydra._internal.config import HydraInputConfig, HydraInputOptions

# TODO: Update when Pydantic supports Python 3.14 (sources and duties as well).
try:
    from pydantic import TypeAdapter
except ImportError:
    TypeAdapter = None


_logger = get_plugin_logger(__name__)


def on_post_build(config: MkDocsConfig, **kwargs: Any) -> None:  # noqa: ARG001
    """Write `schema.json` to the site directory."""
    if TypeAdapter is None:
        _logger.info("Pydantic is not installed, skipping JSON schema generation")
        return

    @dataclass
    class HydraHandlerSchema:
        hydra: HydraInputConfig

    adapter = TypeAdapter(HydraHandlerSchema)
    schema = adapter.json_schema()
    schema["$schema"] = "https://json-schema.org/draft-07/schema"
    with open(join(config.site_dir, "schema.json"), "w") as file:
        json.dump(schema, file, indent=2)
        _logger.debug("Generated JSON schema")

    autorefs = config["plugins"]["autorefs"]
    for field in fields(HydraInputConfig):  # type: ignore[arg-type]
        if f"setting-{field.name}" not in autorefs._primary_url_map:
            _logger.warning(f"Handler setting `{field.name}` is not documented")
    for field in fields(HydraInputOptions):  # type: ignore[arg-type]
        if f"option-{field.name}" not in autorefs._primary_url_map:
            _logger.warning(f"Configuration option `{field.name}` is not documented")

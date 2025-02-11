import logging
from typing import Any

from jsonschema import validate

schema = {
    "type": "object",
    "properties": {
        "teams": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "team_dashboards": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "Filename": {"type": "string"},
                                "filter": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "integrations": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "connector": {"type": "string"},
                    "public_repositories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "optional": True,
                    },
                    "membership_repositories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "optional": True,
                    },
                },
            },
        },
        "config": {
            "type": "object",
            "properties": {
                "google": {
                    "type": "object",
                    "properties": {
                        "app_credentials_file": {
                            "type": "string",
                            "description": "Path to the Google app credentials file",
                        },
                        "token_file": {
                            "type": "string",
                            "description": "Path to the Google OAuth token file",
                        },
                    },
                },
            },
        },
    },
}


def validate_configuration(configuration: Any) -> None:
    """Validates configuration (parsed YAML) against schema.

    Raises:
      ValidationError:
        In case configuration is not valid against schema
    """
    validate(instance=configuration, schema=schema)
    logging.debug("valid configuration: %s", str(configuration))

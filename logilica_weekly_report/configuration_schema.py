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
                            "properties": {"Filename": {"type": "string"}},
                        },
                    },
                    "jira_projects": {"type": "string"},
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
                    "projects": {
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
                    "required": ["app_credentials_file", "token_file"],
                },
            },
            "required": ["google"],
        },
    },
    "required": ["teams", "integrations", "config"],
}

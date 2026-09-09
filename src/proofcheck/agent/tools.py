from typing import Any


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return the bounded tool contracts exposed to the investigation agent."""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_evidence",
                "description": (
                    "Search the supplied project evidence for information "
                    "relevant to the claim."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The evidence question to investigate.",
                        },
                        "document_type": {
                            "type": "string",
                            "description": (
                                "Optional document type filter, such as "
                                "CONTRACT, BOQ, APPROVED_CHANGE, WORK_RECORD, "
                                "INVOICE, or CORRESPONDENCE."
                            ),
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "check_required_evidence",
                "description": (
                    "Check whether the evidence types required for the "
                    "investigation are present."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "required_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Evidence types required for the claim.",
                        },
                        "present_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Evidence types found so far.",
                        },
                    },
                    "required": ["required_types", "present_types"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compare_evidence",
                "description": (
                    "Deterministically compare two numeric evidence values."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expected_value": {
                            "type": "number",
                            "description": "Expected numeric value.",
                        },
                        "observed_value": {
                            "type": "number",
                            "description": "Observed numeric value.",
                        },
                        "unit": {
                            "type": "string",
                            "description": "Unit for the compared values.",
                        },
                    },
                    "required": ["expected_value", "observed_value"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "validate_calculation",
                "description": (
                    "Deterministically validate quantity multiplied by unit "
                    "price against an observed total."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "quantity": {
                            "type": "number",
                            "description": "Quantity being validated.",
                        },
                        "unit_price": {
                            "type": "number",
                            "description": "Unit price being validated.",
                        },
                        "observed_total": {
                            "type": "number",
                            "description": "Total stated in the evidence.",
                        },
                    },
                    "required": ["quantity", "unit_price", "observed_total"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_review_report",
                "description": (
                    "Package the completed investigation into a structured "
                    "review report for human review."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": [
                                "SUPPORTED",
                                "REVIEW_REQUIRED",
                                "BLOCKED",
                            ],
                        },
                        "confidence": {
                            "type": "number",
                            "description": (
                                "Explainable confidence heuristic between 0 and 1."
                            ),
                        },
                        "summary": {
                            "type": "string",
                            "description": "Concise evidence-backed summary.",
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "Recommendation for human review.",
                        },
                    },
                    "required": [
                        "status",
                        "confidence",
                        "summary",
                        "recommendation",
                    ],
                },
            },
        },
    ]

def get_investigation_tool_definitions() -> list[dict[str, Any]]:
    """Return only the tools available to the investigation agent."""
    definitions = get_tool_definitions()

    return [
        definition
        for definition in definitions
        if definition["function"]["name"]
        in {
            "search_evidence",
            "check_required_evidence",
            "compare_evidence",
            "validate_calculation",
        }
    ]

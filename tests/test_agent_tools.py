from proofcheck.agent.tools import get_tool_definitions


EXPECTED_TOOLS = {
    "search_evidence",
    "check_required_evidence",
    "compare_evidence",
    "validate_calculation",
    "generate_review_report",
}


def test_agent_exposes_only_approved_tools():
    definitions = get_tool_definitions()

    names = {
        definition["function"]["name"]
        for definition in definitions
    }

    assert names == EXPECTED_TOOLS


def test_agent_tools_have_function_contracts():
    definitions = get_tool_definitions()

    for definition in definitions:
        assert definition["type"] == "function"
        assert "description" in definition["function"]
        assert "parameters" in definition["function"]


def test_search_evidence_requires_query():
    definitions = get_tool_definitions()

    search_tool = next(
        item
        for item in definitions
        if item["function"]["name"] == "search_evidence"
    )

    assert search_tool["function"]["parameters"]["required"] == ["query"]


def test_validation_tools_require_numeric_inputs():
    definitions = get_tool_definitions()

    tools = {
        item["function"]["name"]: item
        for item in definitions
    }

    assert tools["compare_evidence"]["function"]["parameters"]["required"] == [
        "expected_value",
        "observed_value",
    ]

    assert tools["validate_calculation"]["function"]["parameters"]["required"] == [
        "quantity",
        "unit_price",
        "observed_total",
    ]


def test_review_report_has_bounded_status_values():
    definitions = get_tool_definitions()

    report_tool = next(
        item
        for item in definitions
        if item["function"]["name"] == "generate_review_report"
    )

    status_schema = (
        report_tool["function"]["parameters"]["properties"]["status"]
    )

    assert status_schema["enum"] == [
        "SUPPORTED",
        "REVIEW_REQUIRED",
        "BLOCKED",
    ]

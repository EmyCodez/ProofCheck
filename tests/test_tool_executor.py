import pytest

from proofcheck.agent.tool_executor import ToolExecutor


def test_executor_rejects_unknown_tool():
    executor = ToolExecutor(
        retriever=None,
        project_id="project-001",
    )

    with pytest.raises(
        ValueError,
        match="Tool 'unknown_tool' is not approved",
    ):
        executor.execute("unknown_tool", {})


def test_executor_rejects_non_object_arguments():
    executor = ToolExecutor(
        retriever=None,
        project_id="project-001",
    )

    with pytest.raises(
        ValueError,
        match="Tool arguments must be an object",
    ):
        executor.execute("compare_evidence", [])


def test_executor_enforces_tool_call_limit():
    executor = ToolExecutor(
        retriever=None,
        project_id="project-001",
    )

    for _ in range(executor.MAX_TOOL_CALLS):
        result = executor.execute(
            "compare_evidence",
            {
                "expected_value": 100,
                "observed_value": 100,
            },
        )

        assert result.matches is True

    with pytest.raises(
        RuntimeError,
        match="Maximum investigation tool-call limit reached",
    ):
        executor.execute(
            "compare_evidence",
            {
                "expected_value": 100,
                "observed_value": 100,
            },
        )


def test_executor_executes_deterministic_comparison():
    executor = ToolExecutor(
        retriever=None,
        project_id="project-001",
    )

    result = executor.execute(
        "compare_evidence",
        {
            "expected_value": 1300,
            "observed_value": 1500,
            "unit": "m²",
        },
    )

    assert result.matches is False
    assert result.difference == 200


def test_executor_requires_project_id():
    with pytest.raises(
        ValueError,
        match="Project ID must not be empty",
    ):
        ToolExecutor(
            retriever=None,
            project_id="",
        )

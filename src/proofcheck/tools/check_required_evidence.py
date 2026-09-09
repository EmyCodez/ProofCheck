from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceCheckResult:
    """Deterministic result of checking required evidence."""
    complete: bool
    required_types: list[str]
    present_types: list[str]
    missing_types: list[str]


def check_required_evidence(
    required_types: list[str],
    present_types: list[str],
) -> EvidenceCheckResult:
    """
    Check whether all required evidence types are present.
    """

    required = list(dict.fromkeys(required_types))
    present = list(dict.fromkeys(present_types))

    missing = [item for item in required if item not in present]

    return EvidenceCheckResult(
        complete=len(missing) == 0,
        required_types=required,
        present_types=present,
        missing_types=missing,
    )

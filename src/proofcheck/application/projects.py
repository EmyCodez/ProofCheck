from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    project_id: str
    project_name: str
    corpus_dir: Path
    default_claim: str


PROJECTS = {
    "Al Noor Office Building — Flooring Package": ProjectConfig(
        project_id="project-001",
        project_name="Al Noor Office Building — Flooring Package",
        corpus_dir=Path("data/sample_project"),
        default_claim=(
            "Is invoice INV1042 sufficiently supported by the available "
            "project evidence?"
        ),
    ),
}

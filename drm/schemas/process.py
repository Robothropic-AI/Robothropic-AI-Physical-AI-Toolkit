"""Stage 1 output: the Decomposer's structured model of the process."""
from pydantic import Field, model_validator

from .common import Strict


class Stage(Strict):
    id: int = Field(ge=1)
    name: str
    description: str
    actors: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    depends_on: list[int] = []
    source_text: str  # exact input line, so every later claim is traceable


class ProcessModel(Strict):
    process_name: str
    stages: list[Stage] = Field(min_length=1)
    assumptions: list[str] = []  # what the Decomposer had to infer
    ambiguities: list[str] = []  # questions to put back to the partner

    @model_validator(mode="after")
    def _check_graph(self):
        ids = {s.id for s in self.stages}
        if len(ids) != len(self.stages):
            raise ValueError("duplicate stage ids")
        for s in self.stages:
            if missing := set(s.depends_on) - ids:
                raise ValueError(f"stage {s.id} depends on unknown stage(s) {sorted(missing)}")
        return self



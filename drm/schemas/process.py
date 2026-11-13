"""Stage 1 output: the Decomposer's structured model of the process."""
from pydantic import Field, model_validator

from .common import Strict


class ReworkEdge(Strict):
    """A loop-back and the condition that triggers it."""
    to: int = Field(ge=1)
    when: str = Field(min_length=1)  # e.g. "optical QC fails and the lot is reworked"


class Stage(Strict):
    id: int = Field(ge=1)
    name: str
    description: str
    actors: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    depends_on: list[int] = []  # forward dependencies only: must form a DAG
    rework_to: list[ReworkEdge] = []  # explicit loop-backs, each with its trigger condition
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
            if s.id in s.depends_on:
                raise ValueError(f"stage {s.id} depends on itself")
            if missing := {e.to for e in s.rework_to} - ids:
                raise ValueError(f"stage {s.id} reworks to unknown stage(s) {sorted(missing)}")
            if any(e.to > s.id for e in s.rework_to):
                raise ValueError(f"stage {s.id}: rework_to must point to an earlier or same stage")
        self._require_acyclic({s.id: list(s.depends_on) for s in self.stages})
        return self

    @staticmethod
    def _require_acyclic(graph: dict[int, list[int]]) -> None:
        """Loops must be declared via rework_to, never hidden inside depends_on."""
        state: dict[int, int] = {}  # 1 = visiting, 2 = done

        def visit(n: int) -> None:
            if state.get(n) == 2:
                return
            if state.get(n) == 1:
                raise ValueError("depends_on contains a cycle; declare loop-backs with rework_to")
            state[n] = 1
            for m in graph[n]:
                visit(m)
            state[n] = 2

        for n in graph:
            visit(n)


"""Human approval gate: a ProcessModel is only 'approved' once every open question is resolved.

The Decomposer raises ambiguities; a process engineer answers them. Nothing downstream
should treat a model as final until it is wrapped in an ApprovedProcessModel.
"""
from pydantic import Field, model_validator

from .common import Strict
from .process import ProcessModel


class Resolution(Strict):
    question: str = Field(min_length=1)  # must match an ambiguity of the process model exactly
    answer: str = Field(min_length=1)


class ApprovedProcessModel(Strict):
    process: ProcessModel
    resolutions: list[Resolution] = []
    approved_by: str = Field(min_length=1)  # a named human, never the model

    @model_validator(mode="after")
    def _all_ambiguities_resolved(self):
        asked = set(self.process.ambiguities)
        answered = {r.question for r in self.resolutions}
        if unknown := answered - asked:
            raise ValueError(f"resolutions for questions that were never raised: {sorted(unknown)}")
        if unresolved := asked - answered:
            raise ValueError(f"{len(unresolved)} unresolved ambiguity(ies); first: {sorted(unresolved)[0]}")
        return self



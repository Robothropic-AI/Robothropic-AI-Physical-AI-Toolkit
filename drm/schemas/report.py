"""Stage 3 output: the Synthesizer's report."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .analysis import StageAnalysis
from .approval import Resolution
from .common import Strict
from .constraints import HumanOversight
from .process import ProcessModel


class PriorityEntry(Strict):
    stage_id: int
    tier: Annotated[int, Field(ge=1, le=3)]  # 1 = start here; computed in code, not by the model
    rationale: str


class DRMReport(Strict):
    process: ProcessModel
    analyses: list[StageAnalysis]
    provisional: bool  # True until the process model has been approved by a named person
    human_oversight: HumanOversight = HumanOversight.UNSPECIFIED
    resolutions: list[Resolution] = []  # the human answers behind an approved model
    executive_summary: str
    priorities: list[PriorityEntry]
    cross_cutting_risks: list[str] = []
    open_questions_for_partner: list[str] = []
    limitations: str = Field(min_length=1)  # always populated, and written by code, not by the model
    narrative_source: Literal["offline", "model"]  # how the wording was produced

    @model_validator(mode="after")
    def _priorities_cover_every_analysed_stage(self):
        if {p.stage_id for p in self.priorities} != {a.stage_id for a in self.analyses}:
            raise ValueError("priorities must cover exactly the analysed stages")
        return self


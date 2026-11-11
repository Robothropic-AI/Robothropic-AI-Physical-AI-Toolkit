"""Stage 3 output: the Synthesizer's report."""
from typing import Annotated

from pydantic import Field

from .analysis import StageAnalysis
from .common import Strict
from .process import ProcessModel


class PriorityEntry(Strict):
    stage_id: int
    tier: Annotated[int, Field(ge=1, le=3)]  # 1 = start here
    rationale: str


class DRMReport(Strict):
    process: ProcessModel
    analyses: list[StageAnalysis]
    executive_summary: str
    priorities: list[PriorityEntry]
    cross_cutting_risks: list[str] = []
    open_questions_for_partner: list[str] = []
    limitations: str  # always populated: scores are model judgments for engineer review

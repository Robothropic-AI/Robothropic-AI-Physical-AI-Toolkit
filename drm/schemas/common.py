"""Shared building blocks for all DRM schemas."""
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Anchored 1-5 ordinal scale. The meaning of each level is defined in the
# agent prompts, not here. We avoid percentages: an LLM cannot honestly
# justify "73% suitable".
Scale = Annotated[int, Field(ge=1, le=5)]


class Strict(BaseModel):
    """Base model: unknown fields are rejected, so model drift is caught early."""
    model_config = ConfigDict(extra="forbid")


class InterventionType(str, Enum):
    PERCEPTION = "perception"
    REASONING = "reasoning"
    EXECUTION = "execution"
    COMMUNICATION = "communication"
    NONE = "none"  # an honest "no AI role here" is a valid result


class LatencyClass(str, Enum):
    HARD_REALTIME = "hard_realtime"
    NEAR_REALTIME = "near_realtime"
    BATCH = "batch"


class HumanInLoop(str, Enum):
    NONE = "none"
    REVIEW_AFTER = "review_after"
    APPROVE_BEFORE = "approve_before"
    HUMAN_ONLY = "human_only"


class Reversibility(str, Enum):
    REVERSIBLE = "reversible"
    PARTIAL = "partial"
    IRREVERSIBLE = "irreversible"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LayerPlacement(str, Enum):
    """Ties each stage to the fast/slow layer thesis."""
    FAST = "fast"
    SLOW = "slow"
    HUMAN_ONLY = "human_only"

    

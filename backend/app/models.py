from enum import Enum
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ObjectiveRequest(BaseModel):
    objective: str = Field(min_length=12, max_length=2000)
    use_sql: bool = True
    use_rest_api: bool = True


class AgentStep(BaseModel):
    agent: str
    status: RunStatus
    detail: str


class RunResponse(BaseModel):
    id: str
    objective: str
    status: RunStatus
    steps: list[AgentStep]
    result: dict | None = None

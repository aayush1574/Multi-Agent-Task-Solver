import asyncio
from uuid import uuid4

from .models import AgentStep, ObjectiveRequest, RunResponse, RunStatus


class Orchestrator:
    """Deterministic demo orchestrator; replace each worker with an LLM adapter in production."""

    def __init__(self) -> None:
        self.runs: dict[str, RunResponse] = {}
        self.tasks: dict[str, asyncio.Task[None]] = {}

    def create(self, request: ObjectiveRequest) -> RunResponse:
        run = RunResponse(
            id=f"R-{uuid4().hex[:8].upper()}",
            objective=request.objective,
            status=RunStatus.queued,
            steps=[
                AgentStep(agent="Planner", status=RunStatus.queued, detail="Waiting"),
                AgentStep(agent="Researcher", status=RunStatus.queued, detail="Waiting"),
                AgentStep(agent="Analyst", status=RunStatus.queued, detail="Waiting"),
                AgentStep(agent="Synthesizer", status=RunStatus.queued, detail="Waiting"),
            ],
        )
        self.runs[run.id] = run
        return run

    def start(self, run_id: str, request: ObjectiveRequest) -> None:
        task = asyncio.create_task(self.execute(run_id, request))
        self.tasks[run_id] = task
        task.add_done_callback(lambda _: self.tasks.pop(run_id, None))

    async def execute(self, run_id: str, request: ObjectiveRequest) -> None:
        run = self.runs[run_id]
        try:
            run.status = RunStatus.running
            details = [
                "Objective decomposed into evidence, analysis, and recommendation tasks",
                f"Evidence gathered via {self._tool_label(request)}",
                "Opportunities ranked by impact, confidence, and effort",
                "Findings merged into an actionable decision brief",
            ]
            for step, detail in zip(run.steps, details):
                step.status = RunStatus.running
                step.detail = detail
                await asyncio.sleep(0.35)
                step.status = RunStatus.completed
            run.result = {
                "summary": "Validate the highest-impact, most reversible opportunity first.",
                "recommendations": [
                    "Rank options by impact, confidence, and effort.",
                    "Run a 30-day pilot with one accountable owner.",
                    "Review leading indicators weekly and scale only on evidence.",
                ],
                "tools": self._tool_label(request),
            }
            run.status = RunStatus.completed
        except asyncio.CancelledError:
            run.status = RunStatus.failed
            raise
        except Exception:
            run.status = RunStatus.failed
            raise

    @staticmethod
    def _tool_label(request: ObjectiveRequest) -> str:
        tools = [name for enabled, name in [(request.use_sql, "SQL"), (request.use_rest_api, "REST API")] if enabled]
        return " + ".join(tools) if tools else "reasoning only"

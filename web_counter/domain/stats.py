from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_requests: int
    duration_seconds: float
    avg_rps: float
    min_rps: int
    max_rps: int

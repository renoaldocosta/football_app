from pydantic import BaseModel

class MatchSummaryRequest(BaseModel):
    match_id: int

class MatchSummaryResponse(BaseModel):
    summary: str

class PlayerProfileRequest(BaseModel):
    match_id: int
    player_name: str

class PlayerProfileResponse(BaseModel):
    stats: str
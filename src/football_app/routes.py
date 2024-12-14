from fastapi import APIRouter, HTTPException
from football_stats.matches import get_player_stats, PlayerStatsError 
from tools.football import get_match_summary  
from models import MatchSummaryRequest, MatchSummaryResponse, PlayerProfileRequest, PlayerProfileResponse

router = APIRouter()

@router.post("/match_summary", response_model=MatchSummaryResponse)
def match_summary(request: MatchSummaryRequest):
    try:
        summary = get_match_summary(match_id=request.match_id)
        return MatchSummaryResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/player_profile", response_model=PlayerProfileResponse)
def player_profile(request: PlayerProfileRequest):
    try:
        # Chama a função para obter as estatísticas do jogador
        stats = get_player_stats(match_id=request.match_id, player_name=request.player_name)
        
        # Retorna a resposta no formato esperado
        return PlayerProfileResponse(stats=stats)
    except PlayerStatsError as e:
        # Erro customizado relacionado a estatísticas do jogador
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erros gerais
        raise HTTPException(status_code=500, detail=str(e))
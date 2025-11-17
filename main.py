from fastapi import FastAPI, HTTPException
from typing import List, Optional
from models import Card, CardColor
from game_manager import game_manager

app = FastAPI(title="UNO Game API", description="API para gerenciar jogos de UNO")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do UNO!"}

@app.get("/novoJogo")
def novo_jogo(quantidadeJog: int):
    """
    Inicia um novo jogo com a quantidade especificada de jogadores
    Retorna o ID do jogo criado
    """
    try:
        game_id = game_manager.novo_jogo(quantidadeJog)
        return {
            "message": f"Novo jogo criado com {quantidadeJog} jogadores",
            "game_id": game_id,
            "quantidade_jogadores": quantidadeJog
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/jogo/{id_jogo}/jogador_da_vez")
def jogador_da_vez(id_jogo: int):
    """
    Retorna o ID do jogador da vez
    """
    try:
        current_player = game_manager.get_current_player(id_jogo)
        return {
            "game_id": id_jogo,
            "current_player": current_player
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/jogo/{id_jogo}/jogador/{id_jogador}")
def ver_cartas_jogador(id_jogo: int, id_jogador: int):
    """
    Retorna as cartas na mão do jogador especificado
    """
    try:
        cards = game_manager.get_player_hand(id_jogo, id_jogador)
        return {
            "game_id": id_jogo,
            "player_id": id_jogador,
            "cards": [str(card) for card in cards],
            "card_count": len(cards)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/jogo/{id_jogo}/jogar")
def jogar_carta(id_jogo: int, id_jogador: int, id_carta: int,
    cor_escolhida: Optional[CardColor] = None):
    """
    Joga uma carta da mão do jogador
    """
    try:
        result = game_manager.jogar_carta(id_jogo, id_jogador, id_carta, cor_escolhida)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/jogo/{id_jogo}/passa")
def passar_vez(id_jogo: int, id_jogador: int):
    """
    Passa a vez, comprando uma carta
    """
    try:
        result = game_manager.passar_vez(id_jogo, id_jogador)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rota adicional para debug - visualizar estado completo do jogo
@app.get("/debug/jogo/{id_jogo}")
def debug_game_state(id_jogo: int):
    """
    Rota para debug - retorna o estado completo do jogo
    """
    game_state = game_manager.get_game_state(id_jogo)
    if not game_state:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    
    return {
        "game_id": game_state.id,
        "status": game_state.status,
        "current_player": game_state.current_player_index,
        "top_discard_card": str(game_state.get_top_discard_card()) if game_state.get_top_discard_card() else None,
        "deck_size": len(game_state.deck),
        "discard_pile_size": len(game_state.discard_pile),
        "players": [
            {
                "player_id": player.id,
                "card_count": len(player.hand),
                "cards": [str(card) for card in player.hand]
            }
            for player in game_state.players
        ],
        "winner": game_state.winner
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
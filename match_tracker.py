from typing import Dict, Any
from models import GameState, GameStatus
from observer_pattern import Observer

class MatchTracker(Observer):
    """
    Este é o Observador Concreto.
    Ele rastreia as partidas em andamento e finalizadas.
    """
    def __init__(self):
        # Usamos dicionários para armazenar um resumo do estado
        self.games_in_progress: Dict[int, Dict[str, Any]] = {}
        self.games_finished: Dict[int, Dict[str, Any]] = {}

    def update(self, game_state: GameState):
        """
        Este método é chamado pelo GameManager (Subject)
        quando um jogo muda de estado.
        """
        game_id = game_state.id
        
        if game_state.status == GameStatus.IN_PROGRESS:
            # Se o jogo começou, adiciona aos "em andamento"
            self.games_in_progress[game_id] = self._summarize_state(game_state)
            
            # Garante que não está na lista de finalizados (caso seja um re-match, etc)
            if game_id in self.games_finished:
                del self.games_finished[game_id]

        elif game_state.status == GameStatus.FINISHED:
            # Se o jogo terminou, move para "finalizados"
            self.games_finished[game_id] = self._summarize_state(game_state)
            
            # Remove dos "em andamento"
            if game_id in self.games_in_progress:
                del self.games_in_progress[game_id]
                
    def _summarize_state(self, game_state: GameState) -> Dict[str, Any]:
        """Cria um resumo simples do estado do jogo."""
        # A "rodada" pode ser interpretada como quem é o jogador da vez
        # ou o número de cartas jogadas. Vou focar no status e no jogador atual.
        return {
            "game_id": game_state.id,
            "status": game_state.status.value,
            "current_player_turn": game_state.current_player_index,
            "player_count": len(game_state.players),
            "top_card": str(game_state.get_top_discard_card()),
            "winner": game_state.winner
        }

    def get_match_stats(self) -> Dict[str, Any]:
        """Retorna as estatísticas para a rota da API."""
        return {
            "total_partidas_ativas": len(self.games_in_progress),
            "total_partidas_finalizadas": len(self.games_finished),
            "partidas_em_andamento": list(self.games_in_progress.values()),
            "partidas_finalizadas": list(self.games_finished.values())
        }

import pytest
from game_manager import GameManager
from match_tracker import MatchTracker
from models import Card, CardType, GameStatus

# Fixture mais complexa: prepara o manager, o tracker e conecta-os
@pytest.fixture
def setup_observer():
    """Prepara um GameManager e um MatchTracker conectados."""
    manager = GameManager()
    tracker = MatchTracker()
    manager.attach(tracker)
    return manager, tracker

def test_observer_novo_jogo(setup_observer):
    """Testa se o tracker regista um jogo novo."""
    manager, tracker = setup_observer
    
    # Antes de tudo, o tracker está vazio
    stats_antes = tracker.get_match_stats()
    assert stats_antes["total_partidas_ativas"] == 0
    
    # Ação: Criar um novo jogo
    manager.novo_jogo(quantidade_jogadores=2)
    
    # Verificação: O tracker deve ter registado o jogo
    stats_depois = tracker.get_match_stats()
    assert stats_depois["total_partidas_ativas"] == 1
    assert stats_depois["partidas_em_andamento"][0]["game_id"] == 1
    assert stats_depois["partidas_em_andamento"][0]["status"] == GameStatus.IN_PROGRESS

def test_observer_jogo_finalizado(setup_observer):
    """Testa se o tracker move o jogo de 'em_andamento' para 'finalizado'."""
    manager, tracker = setup_observer
    
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    
    # Jogo está em andamento
    stats_meio = tracker.get_match_stats()
    assert stats_meio["total_partidas_ativas"] == 1
    assert stats_meio["total_partidas_finalizadas"] == 0
    
    # Simula uma vitória (copiado do test_game_manager)
    game = manager.get_game_state(game_id)
    player_0 = game.players[0]
    top_card = game.get_top_discard_card()
    player_0.hand = []
    player_0.add_card(Card(id=99, color=top_card.color, type=CardType.NUMBER, value=1))
    
    # Ação: Jogar a carta da vitória
    manager.jogar_carta(game_id, player_id=0, card_index=0)
    
    # Verificação: O tracker deve ter atualizado o status
    stats_fim = tracker.get_match_stats()
    assert stats_fim["total_partidas_ativas"] == 0
    assert stats_fim["total_partidas_finalizadas"] == 1
    assert stats_fim["partidas_finalizadas"][0]["game_id"] == 1
    assert stats_fim["partidas_finalizadas"][0]["status"] == GameStatus.FINISHED
    assert stats_fim["partidas_finalizadas"][0]["winner"] == 0
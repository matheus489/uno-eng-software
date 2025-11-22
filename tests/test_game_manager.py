import pytest
from game_manager import GameManager
from models import Card, CardColor, CardType
from models import GameStatus
from card_effects import NumberCardEffect

@pytest.fixture
def manager():
    """Cria uma instância limpa do GameManager para cada teste."""
    return GameManager()

def test_novo_jogo(manager: GameManager):
    """Testa se o novo_jogo cria o estado corretamente."""
    game_id = manager.novo_jogo(quantidade_jogadores=4)
    
    assert game_id == 1
    game_state = manager.get_game_state(game_id)
    
    assert game_state is not None
    assert game_state.status == GameStatus.IN_PROGRESS
    assert len(game_state.players) == 4
    
    for player in game_state.players:
        assert len(player.hand) == 5
    
    assert len(game_state.discard_pile) == 1

def test_jogar_carta_valida(manager: GameManager):
    """Testa uma jogada válida e a passagem de turno."""
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    game = manager.get_game_state(game_id)
    
    top_card = game.get_top_discard_card()
    
    carta_limpa = Card(
        id=999, 
        color=top_card.color, 
        type=CardType.NUMBER, 
        value=5
    )
    
    carta_limpa.effect_strategy = NumberCardEffect()

    game.players[0].hand.insert(0, carta_limpa)
    
    result = manager.jogar_carta(game_id, player_id=0, card_index=0)
    
    assert result["message"] == "Carta jogada com sucesso"
    
    assert game.current_player_index == 1

def test_jogar_carta_turno_errado(manager: GameManager):
    """Testa se o jogo bloqueia um jogador fora do seu turno."""
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    
    with pytest.raises(ValueError, match="Não é a vez deste jogador"):
        manager.jogar_carta(game_id, player_id=1, card_index=0)

def test_jogar_carta_errada(manager: GameManager):
    """Testa se o jogo bloqueia uma carta que não combina."""
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    game = manager.get_game_state(game_id)
    
    top_card = game.get_top_discard_card()

    carta_invalida = game.players[0].hand[0]

    carta_invalida.type = CardType.NUMBER

    # Garante que a carta é inválida (cor e valor diferente)
    carta_invalida.color = CardColor.GREEN if top_card.color != CardColor.GREEN else CardColor.BLUE
    carta_invalida.value = 1 if top_card.value != 1 else 2
    
    with pytest.raises(ValueError, match="Carta não pode ser jogada"):
        manager.jogar_carta(game_id, player_id=0, card_index=0)

def test_passar_vez(manager: GameManager):
    """Testa se o jogador compra uma carta e o turno passa."""
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    game = manager.get_game_state(game_id)
    
    player_0_hand_count = len(game.players[0].hand)
    deck_count = len(game.deck)
    
    manager.passar_vez(game_id, player_id=0)
    
    # Verifica se o jogador 0 comprou uma carta
    assert len(game.players[0].hand) == player_0_hand_count + 1
    # Verifica se o deck diminuiu
    assert len(game.deck) == deck_count - 1
    # Verifica se o turno passou
    assert game.current_player_index == 1

def test_vitoria_jogo(manager: GameManager):
    """Testa a condição de vitória."""
    game_id = manager.novo_jogo(quantidade_jogadores=2)
    game = manager.get_game_state(game_id)
    
    # Simula um jogador prestes a ganhar
    player_0 = game.players[0]
    top_card = game.get_top_discard_card()
    
    # Esvazia a mão do jogador
    player_0.hand = []
    
    # Adiciona uma única carta jogável
    carta_jogavel = Card(id=99, color=top_card.color, type=CardType.NUMBER, value=1)
    player_0.add_card(carta_jogavel)
    
    # O jogador 0 joga a sua última carta (índice 0)
    result = manager.jogar_carta(game_id, player_id=0, card_index=0)
    
    assert result["game_finished"] == True
    assert result["winner"] == 0
    assert game.status == GameStatus.FINISHED
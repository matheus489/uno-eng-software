import pytest
from unittest.mock import Mock
from card_effects import (
    CardEffectFactory, 
    NumberCardEffect, 
    SkipCardEffect, 
    ReverseCardEffect, 
    DrawTwoCardEffect, 
    WildCardEffect, 
    WildDrawFourCardEffect
)
from models import Card, CardColor, CardType, GameState

@pytest.fixture
def mock_game():
    """Cria um GameState falso (Mock) para verificarmos as chamadas."""
    return Mock(spec=GameState)

def test_factory_creates_correct_instances():
    """Testa se a fábrica retorna a classe correta para cada tipo de carta."""
    assert isinstance(CardEffectFactory.create_effect(CardType.NUMBER), NumberCardEffect)
    assert isinstance(CardEffectFactory.create_effect(CardType.SKIP), SkipCardEffect)
    assert isinstance(CardEffectFactory.create_effect(CardType.REVERSE), ReverseCardEffect)
    assert isinstance(CardEffectFactory.create_effect(CardType.DRAW_TWO), DrawTwoCardEffect)
    assert isinstance(CardEffectFactory.create_effect(CardType.WILD), WildCardEffect)
    assert isinstance(CardEffectFactory.create_effect(CardType.WILD_DRAW_FOUR), WildDrawFourCardEffect)


def test_can_play_same_color():
    """Testa se pode jogar carta da mesma cor (Strategy Base)."""
    effect = NumberCardEffect()
    card = Card(id=1, color=CardColor.RED, type=CardType.NUMBER, value=5)
    top_card = Card(id=2, color=CardColor.RED, type=CardType.NUMBER, value=2)
    
    assert effect.can_play(card, top_card) is True

def test_can_play_same_type():
    """Testa se pode jogar carta do mesmo tipo (Strategy Base)."""
    effect = SkipCardEffect() 
    card = Card(id=1, color=CardColor.BLUE, type=CardType.SKIP)
    top_card = Card(id=2, color=CardColor.RED, type=CardType.SKIP)
    
    assert effect.can_play(card, top_card) is True

def test_cannot_play_different_color_and_type():
    """Testa bloqueio de carta diferente."""
    effect = NumberCardEffect()
    card = Card(id=1, color=CardColor.BLUE, type=CardType.NUMBER, value=5)
    top_card = Card(id=2, color=CardColor.RED, type=CardType.NUMBER, value=2)
    
    assert effect.can_play(card, top_card) is False

def test_wild_always_playable():
    """Testa se cartas coringas sempre podem ser jogadas."""
    wild_effect = WildCardEffect()
    wild_card = Card(id=1, color=CardColor.RED, type=CardType.WILD) 
    top_card = Card(id=2, color=CardColor.BLUE, type=CardType.NUMBER, value=9)
    
    assert wild_effect.can_play(wild_card, top_card) is True

def test_skip_effect_calls_game_method(mock_game):
    """Testa se SkipCardEffect chama game.apply_skip_effect."""
    effect = SkipCardEffect()
    effect.apply_effect(mock_game, player_id=1)
    
    mock_game.apply_skip_effect.assert_called_once()

def test_reverse_effect_calls_game_method(mock_game):
    """Testa se ReverseCardEffect chama game.apply_reverse_effect."""
    effect = ReverseCardEffect()
    effect.apply_effect(mock_game, player_id=1)
    
    mock_game.apply_reverse_effect.assert_called_once()

def test_draw_two_effect_calls_game_method(mock_game):
    """Testa se DrawTwoCardEffect chama game.apply_draw_two_effect."""
    effect = DrawTwoCardEffect()
    effect.apply_effect(mock_game, player_id=1)
    
    mock_game.apply_draw_two_effect.assert_called_once()

def test_wild_effect_calls_game_method(mock_game):
    """Testa se WildCardEffect chama game.apply_wild_effect com a cor escolhida."""
    effect = WildCardEffect()
    chosen_color = CardColor.BLUE
    
    effect.apply_effect(mock_game, player_id=1, chosen_color=chosen_color)
    
    mock_game.apply_wild_effect.assert_called_once_with(chosen_color)

def test_wild_draw_four_effect_calls_game_method(mock_game):
    """Testa se WildDrawFour chama game.apply_wild_draw_four_effect."""
    effect = WildDrawFourCardEffect()
    chosen_color = CardColor.GREEN
    
    effect.apply_effect(mock_game, player_id=1, chosen_color=chosen_color)
    
    mock_game.apply_wild_draw_four_effect.assert_called_once_with(chosen_color)
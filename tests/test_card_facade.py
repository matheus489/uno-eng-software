from models import Card, CardColor, CardType
from card_facade import CardFacade

def test_create_uno_deck():
    """Testa se o baralho é criado com o número correto de cartas."""
    deck = CardFacade.create_uno_deck()
    assert len(deck) == 108

def test_can_play_card_mesma_cor():
    """Testa se pode jogar cartas de mesma cor."""
    top_card = Card(id=1, color=CardColor.RED, type=CardType.NUMBER, value=5)
    card_to_play = Card(id=2, color=CardColor.RED, type=CardType.NUMBER, value=2)
    
    assert CardFacade.can_play_card(card_to_play, top_card) == True

def test_can_play_card_mesmo_valor():
    """Testa se pode jogar cartas de mesmo valor."""
    top_card = Card(id=1, color=CardColor.RED, type=CardType.NUMBER, value=5)
    card_to_play = Card(id=2, color=CardColor.BLUE, type=CardType.NUMBER, value=5)
    
    assert CardFacade.can_play_card(card_to_play, top_card) == True

def test_can_play_card_invalida():
    """Testa se bloqueia uma carta inválida."""
    top_card = Card(id=1, color=CardColor.RED, type=CardType.NUMBER, value=5)
    card_to_play = Card(id=2, color=CardColor.BLUE, type=CardType.NUMBER, value=3)
    
    assert CardFacade.can_play_card(card_to_play, top_card) == False
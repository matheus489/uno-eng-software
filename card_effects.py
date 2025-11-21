from typing import Dict, Any
from abc import ABC, abstractmethod
from models import Card, CardColor, CardType, GameState, CardEffectStrategy

# Strategy Base
class BaseCardEffect(CardEffectStrategy, ABC):
    def can_play(self, Card: Card, top_Card: Card) -> bool:
        """Cartas de ação podem ser jogadas se forem da mesma cor ou do mesmo tipo"""
        return Card.color == top_Card.color or Card.type == top_Card.type

# Efeito para cartas numéricas (sem efeito especial)
class NumberCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int) -> Dict[str, Any]:
        return game.apply_Card_effect(Card(
            id=0, color=Card.color, type=CardType.NUMBER, value=Card.value
        ))

# Efeito para carta Skip (Pular)
class SkipCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int) -> Dict[str, Any]:
        return game.apply_skip_effect()

# Efeito para carta Reverse (Inverter)
class ReverseCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int) -> Dict[str, Any]:
        return game.apply_reverse_effect()

# Efeito para carta Draw Two (+2)
class DrawTwoCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int) -> Dict[str, Any]:
        return game.apply_draw_two_effect()

# Efeito para carta Wild (Curinga)
class WildCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int, chosen_color: CardColor = None) -> Dict[str, Any]:
        return game.apply_wild_effect(chosen_color)
    
    def can_play(self, Card: Card, top_Card: Card) -> bool:
        return True

# Efeito para carta Wild Draw Four (+4 Curinga)
class WildDrawFourCardEffect(BaseCardEffect):
    def apply_effect(self, game: GameState, player_id: int, chosen_color: CardColor = None) -> Dict[str, Any]:
        return game.apply_wild_draw_four_effect(chosen_color)
    
    def can_play(self, Card: Card, top_Card: Card) -> bool:
        return True

# Fábrica de Strategies
class CardEffectFactory:
    @staticmethod
    def create_effect(Card_type: CardType) -> CardEffectStrategy:
        effects = {
            CardType.NUMBER: NumberCardEffect(),
            CardType.SKIP: SkipCardEffect(),
            CardType.REVERSE: ReverseCardEffect(),
            CardType.DRAW_TWO: DrawTwoCardEffect(),
            CardType.WILD: WildCardEffect(),
            CardType.WILD_DRAW_FOUR: WildDrawFourCardEffect()
        }
        return effects.get(Card_type, NumberCardEffect())
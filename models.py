from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional, Dict
from pydantic import BaseModel

class CardColor(str, Enum):
    RED = "RED"
    BLUE = "BLUE" 
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    WILD = "WILD"

class CardType(str, Enum):
    NUMBER = "NUMBER"
    SKIP = "SKIP"
    REVERSE = "REVERSE"
    DRAW_TWO = "DRAW_TWO"
    WILD = "WILD"
    WILD_DRAW_FOUR = "WILD_DRAW_FOUR"
    
class PlayDirection(str, Enum):
    CLOCKWISE = "CLOCKWISE"
    COUNTER_CLOCKWISE = "COUNTER_CLOCKWISE"
    
class CardEffectStrategy(ABC):
    @abstractmethod
    def apply_effect(self, game: 'GameState', player_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def can_play(self, card: 'Card', top_card: 'Card') -> bool:
        pass

class Card(BaseModel):
    id: int
    color: CardColor
    type: CardType
    value: Optional[int] = None  # Para cartas numéricas (0-9)
    effect_strategy: Optional[CardEffectStrategy] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __str__(self):
        if self.type == CardType.NUMBER:
            return f"{self.color.value}_{self.value}"
        else:
            return f"{self.color.value}_{self.type.value}"
        
    def apply_effect(self, game: 'GameState', player_id: int) -> Dict[str, Any]:
        if self.effect_strategy:
            return self.effect_strategy.apply_effect(game, player_id)
        return {"message": "Nenhum efeito aplicado"}
    
    def can_play(self, top_card: 'Card') -> bool:
        if self.effect_strategy:
            return self.effect_strategy.can_play(self, top_card)
        return False

class Player(BaseModel):
    id: int
    hand: List[Card] = []
    
    def add_card(self, card: Card):
        self.hand.append(card)
    
    def remove_card(self, card_index: int) -> Optional[Card]:
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None
    
    def has_cards(self) -> bool:
        return len(self.hand) > 0
    
    def get_card_count(self) -> int:
        return len(self.hand)

class GameStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"

class GameState(BaseModel):
    id: int
    players: List[Player]
    deck: List[Card]
    discard_pile: List[Card]
    current_player_index: int
    status: GameStatus
    winner: Optional[int] = None
    play_direction: PlayDirection = PlayDirection.CLOCKWISE
    current_color: Optional[CardColor] = None
    
    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def get_top_discard_card(self) -> Optional[Card]:
        if self.discard_pile:
            return self.discard_pile[-1]
        return None
    
    def next_turn(self):
        """Avança para o próximo jogador de acordo com a direção do jogo"""
        if self.play_direction == PlayDirection.CLOCKWISE:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        else:
            self.current_player_index = (self.current_player_index - 1) % len(self.players)
    
    def reverse_direction(self):
        """Inverte a direção do jogo - Ação da carta REVERSE"""
        if self.play_direction == PlayDirection.CLOCKWISE:
            self.play_direction = PlayDirection.COUNTER_CLOCKWISE
        else:
            self.play_direction = PlayDirection.CLOCKWISE
        
        # Em jogos com 2 jogadores, Reverse age como Skip
        if len(self.players) == 2:
            self.next_turn()
    
    def skip_player(self):
        """Pula o próximo jogador - Ação da carta SKIP"""
        self.next_turn()  # Avança mais uma vez para pular o próximo
    
    def draw_cards_for_player(self, player_id: int, quantity: int) -> List[Card]:
        """Faz um jogador comprar cartas - Ação das cartas DRAW TWO e WILD DRAW FOUR"""
        cards_drawn = []
        for _ in range(quantity):
            if self.deck:
                card = self.deck.pop()
                self.players[player_id].add_card(card)
                cards_drawn.append(card)
            else:
                # Se o deck acabar, reinicia com as cartas de descarte (exceto a do topo)
                self._replenish_deck_from_discard()
                if self.deck:
                    card = self.deck.pop()
                    self.players[player_id].add_card(card)
                    cards_drawn.append(card)
        return cards_drawn
    
    def _replenish_deck_from_discard(self):
        """Reabastece o deck com as cartas da pilha de descarte (exceto a do topo)"""
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()  # Mantém a carta do topo
            self.deck = self.discard_pile.copy()  # Usa o resto para o deck
            self.discard_pile = [top_card]  # Recria a pilha de descarte apenas com a carta do topo
            
            import random
            random.shuffle(self.deck)
    
    def set_current_color(self, color: CardColor):
        """Define a cor atual - Ação das cartas WILD e WILD DRAW FOUR"""
        self.current_color = color
    
    def apply_skip_effect(self) -> Dict[str, Any]:
        """Aplica o efeito da carta SKIP"""
        skipped_player = self.current_player_index
        self.skip_player()
        self.skip_player()
        
        return {
            "message": f"Jogador {skipped_player} pulado!",
            "effect": "skip",
            "skipped_player": skipped_player,
            "next_player": self.current_player_index
        }
    
    def apply_reverse_effect(self) -> Dict[str, Any]:
        """Aplica o efeito da carta REVERSE"""
        old_direction = self.play_direction
        self.reverse_direction()
        self.skip_player()
        
        result = {
            "message": f"Direção do jogo invertida de {old_direction.value} para {self.play_direction.value}!",
            "effect": "reverse",
            "old_direction": old_direction.value,
            "new_direction": self.play_direction.value,
            "next_player": self.current_player_index
        }
        
        # Em jogos com 2 jogadores, Reverse age como Skip
        if len(self.players) == 2:
            result["message"] = "Em 2 jogadores, Reverse age como Skip! Próximo jogador pulado."
            result["effect"] = "reverse_as_skip"
        
        return result
    
    def apply_draw_two_effect(self) -> Dict[str, Any]:
        """Aplica o efeito da carta DRAW TWO"""
        self.skip_player()
        target_player = self.current_player_index
        cards_drawn = self.draw_cards_for_player(target_player, 2)
        
        return {
            "message": f"Jogador {target_player} comprou 2 cartas e perdeu a vez!",
            "effect": "draw_two",
            "target_player": target_player,
            "cards_drawn": [str(card) for card in cards_drawn],
            "next_player": self.current_player_index
        }
    
    def apply_wild_effect(self, chosen_color: CardColor = None) -> Dict[str, Any]:
        """Aplica o efeito da carta WILD"""
        if chosen_color:
            self.set_current_color(chosen_color)
            self.skip_player()
            return {
                "message": f"Cor mudada para {chosen_color.value}!",
                "effect": "wild",
                "new_color": chosen_color.value,
                "next_player": self.current_player_index
            }
        else:
            return {
                "message": "Carta curinga jogada - cor deve ser escolhida",
                "effect": "wild_choose_color",
                "next_player": self.current_player_index
            }
    
    def apply_wild_draw_four_effect(self, chosen_color: CardColor = None) -> Dict[str, Any]:
        """Aplica o efeito da carta WILD DRAW FOUR"""
        self.skip_player()  # Pula o jogador que comprou as cartas
        target_player = self.current_player_index
        cards_drawn = self.draw_cards_for_player(target_player, 4)
        
        result = {
            "message": f"Jogador {target_player} comprou 4 cartas e perdeu a vez!",
            "effect": "wild_draw_four",
            "target_player": target_player,
            "cards_drawn": [str(card) for card in cards_drawn],
            "next_player": self.current_player_index
        }
        
        if chosen_color:
            self.set_current_color(chosen_color)
            result["new_color"] = chosen_color.value
            result["message"] += f" Cor mudada para {chosen_color.value}!"
        
        return result
    
    def apply_card_effect(self, card: Card, chosen_color: CardColor = None) -> Dict[str, Any]:
        """Aplica o efeito de uma carta baseado no seu tipo"""
        if card.type == CardType.SKIP:
            return self.apply_skip_effect()
        elif card.type == CardType.REVERSE:
            return self.apply_reverse_effect()
        elif card.type == CardType.DRAW_TWO:
            return self.apply_draw_two_effect()
        elif card.type == CardType.WILD:
            return self.apply_wild_effect(chosen_color)
        elif card.type == CardType.WILD_DRAW_FOUR:
            return self.apply_wild_draw_four_effect(chosen_color)
        else:
            # Para cartas numéricas, apenas passa a vez
            self.next_turn()
            return {
                "message": "Carta numérica jogada",
                "effect": "none",
                "next_player": self.current_player_index
            }
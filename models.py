from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel

class CardColor(str, Enum):
    RED = "RED"
    BLUE = "BLUE" 
    GREEN = "GREEN"
    YELLOW = "YELLOW"

class CardType(str, Enum):
    NUMBER = "NUMBER"
    SKIP = "SKIP"
    REVERSE = "REVERSE"
    DRAW_TWO = "DRAW_TWO"
    WILD = "WILD"
    WILD_DRAW_FOUR = "WILD_DRAW_FOUR"

class Card(BaseModel):
    id: int
    color: CardColor
    type: CardType
    value: Optional[int] = None  # Para cartas numéricas (0-9)
    
    def __str__(self):
        if self.type == CardType.NUMBER:
            return f"{self.color.value}_{self.value}"
        else:
            return f"{self.color.value}_{self.type.value}"

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
    
    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def get_top_discard_card(self) -> Optional[Card]:
        if self.discard_pile:
            return self.discard_pile[-1]
        return None
    
    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
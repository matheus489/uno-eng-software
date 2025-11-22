from typing import List, Optional
from models import Card, CardColor, CardType, GameState
from card_effects import CardEffectFactory

class CardFacade:
    """
    Fachada para operações relacionadas a cartas do UNO.
    Centraliza toda a lógica de manipulação e validação de cartas.
    """
    
    @staticmethod
    def create_uno_deck() -> List[Card]:
        """
        Cria um baralho completo de UNO sem cartas especiais
        Retorna: Lista de cartas ordenadas
        """
        deck = []
        card_id = 0
        
        for color in [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]:
            deck.append(Card(
                id=card_id, 
                color=color, 
                type=CardType.NUMBER, 
                value=0,
                effect_strategy=CardEffectFactory.create_effect(CardType.NUMBER)
            ))
            card_id += 1
            
            for value in range(1, 10):
                deck.append(Card(
                    id=card_id, 
                    color=color, 
                    type=CardType.NUMBER, 
                    value=value,
                    effect_strategy=CardEffectFactory.create_effect(CardType.NUMBER)
                ))
                card_id += 1
                deck.append(Card(
                    id=card_id, 
                    color=color, 
                    type=CardType.NUMBER, 
                    value=value,
                    effect_strategy=CardEffectFactory.create_effect(CardType.NUMBER)
                ))
                card_id += 1
        
        action_cards = [
            (CardType.SKIP, 2),
            (CardType.REVERSE, 2), 
            (CardType.DRAW_TWO, 2)
        ]
        
        for color in [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]:
            for card_type, quantity in action_cards:
                for _ in range(quantity):
                    deck.append(Card(
                        id=card_id,
                        color=color,
                        type=card_type,
                        effect_strategy=CardEffectFactory.create_effect(card_type)
                    ))
                    card_id += 1
        
        # Cartas curinga (4 de cada) - FORA DE TODOS OS LOOPS
        wild_cards = [
            (CardType.WILD, 4),
            (CardType.WILD_DRAW_FOUR, 4)
        ]
        
        for card_type, quantity in wild_cards:
            for _ in range(quantity):
                deck.append(Card(
                    id=card_id,
                    color=CardColor.WILD,
                    type=card_type,
                    effect_strategy=CardEffectFactory.create_effect(card_type)
                ))
                card_id += 1
        
        return deck
    
    @staticmethod
    def can_play_card(card: Card, top_card: Card, current_color: Optional[CardColor] = None) -> bool:
        """
        Verifica se uma carta pode ser jogada sobre a carta do topo
        Considera a cor atual para cartas curinga
        """

        if card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return True
        
        effective_top_color = current_color if current_color else top_card.color
        
        if effective_top_color == CardColor.WILD:
            return False
            
        if card.color == effective_top_color:
            return True

        if card.type == top_card.type:
            if card.type == CardType.NUMBER:
                return card.value == top_card.value
            return True
            
        return False
    
    @staticmethod
    def apply_card_effect(card: Card, game: GameState, player_id: int, **kwargs) -> dict:
        """
        Aplica o efeito da carta usando a strategy
        """
        return card.apply_effect(game, player_id)
    
    @staticmethod
    def get_card_display_name(card: Card) -> str:
        """
        Retorna uma representação em string da carta
        """
        if card.type == CardType.NUMBER:
            return f"{card.color.value}_{card.value}"
        else:
            return f"{card.color.value}_{card.type.value}"
    
    @staticmethod
    def get_card_point_value(card: Card) -> int:
        """
        Retorna o valor em pontos da carta
        """
        if card.type == CardType.NUMBER:
            return card.value or 0
        elif card.type in [CardType.SKIP, CardType.REVERSE, CardType.DRAW_TWO]:
            return 20
        elif card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return 50
        else:
            return 0
    
    @staticmethod
    def filter_playable_cards(hand: List[Card], top_card: Card, current_color: Optional[CardColor] = None) -> List[Card]:
        """
        Filtra as cartas jogáveis da mão do jogador
        """
        return [card for card in hand if CardFacade.can_play_card(card, top_card, current_color)]
    
    @staticmethod
    def has_playable_cards(hand: List[Card], top_card: Card, current_color: Optional[CardColor] = None) -> bool:
        """
        Verifica se o jogador tem cartas jogáveis
        """
        return any(CardFacade.can_play_card(card, top_card, current_color) for card in hand)
    
    @staticmethod
    def calculate_hand_value(hand: List[Card]) -> int:
        """
        Calcula o valor total em pontos de uma mão de cartas
        """
        return sum(CardFacade.get_card_point_value(card) for card in hand)
    
    @staticmethod
    def validate_card_index(hand: List[Card], card_index: int) -> bool:
        """
        Valida se o índice da carta é válido para a mão
        """
        return 0 <= card_index < len(hand)
    
    @staticmethod
    def get_card_by_index(hand: List[Card], card_index: int) -> Optional[Card]:
        """
        Retorna uma carta pelo índice, se existir
        """
        if CardFacade.validate_card_index(hand, card_index):
            return hand[card_index]
        return None
    
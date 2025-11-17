from typing import List, Optional
from models import Card, CardColor, CardType

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
        
        # Cartas numéricas (0-9) para cada cor
        for color in CardColor:
            # Uma carta 0 de cada cor
            deck.append(Card(
                id=card_id, 
                color=color, 
                type=CardType.NUMBER, 
                value=0
            ))
            card_id += 1
            
            # Duas cartas de 1-9 de cada cor
            for value in range(1, 10):
                deck.append(Card(
                    id=card_id, 
                    color=color, 
                    type=CardType.NUMBER, 
                    value=value
                ))
                card_id += 1
                deck.append(Card(
                    id=card_id, 
                    color=color, 
                    type=CardType.NUMBER, 
                    value=value
                ))
                card_id += 1
        
        return deck
    
    @staticmethod
    def can_play_card(card: Card, top_card: Card) -> bool:
        """
        Verifica se uma carta pode ser jogada sobre a carta do topo
        Regras: mesma cor OU mesmo valor (para cartas numéricas)
        """
        # Cartas podem ser jogadas se forem da mesma cor
        if card.color == top_card.color:
            return True
        
        # Ou se forem cartas numéricas com o mesmo valor
        if (card.type == CardType.NUMBER and 
            top_card.type == CardType.NUMBER and 
            card.value == top_card.value):
            return True
        
        return False
    
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
        # Para futuras cartas especiais
        elif card.type in [CardType.SKIP, CardType.REVERSE, CardType.DRAW_TWO]:
            return 20
        elif card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return 50
        else:
            return 0
    
    @staticmethod
    def filter_playable_cards(hand: List[Card], top_card: Card) -> List[Card]:
        """
        Filtra as cartas jogáveis da mão do jogador
        Retorna: Lista de cartas que podem ser jogadas
        """
        return [card for card in hand if CardFacade.can_play_card(card, top_card)]
    
    @staticmethod
    def has_playable_cards(hand: List[Card], top_card: Card) -> bool:
        """
        Verifica se o jogador tem cartas jogáveis
        """
        return any(CardFacade.can_play_card(card, top_card) for card in hand)
    
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
    
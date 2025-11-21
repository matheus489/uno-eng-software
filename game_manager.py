import random
from typing import List, Dict, Optional
from models import Card, CardColor, CardType, Player, GameState, GameStatus, PlayDirection
from card_facade import CardFacade

from observer_pattern import Subject, Observer

class GameManager(Subject):
    def __init__(self):
        super().__init__()
        self.games: Dict[int, GameState] = {}
        self.next_game_id = 1

        self._observers: List[Observer] = []

    def notify(self, game_state: GameState):
        """Notifica todos os observadores anexados."""
        for observer in self._observers:
            observer.update(game_state)
    
    def _shuffle_deck(self, deck: List[Card]) -> List[Card]:
        """Embaralha o deck"""
        random.shuffle(deck)
        return deck
    
    def novo_jogo(self, quantidade_jogadores: int) -> int:
        """Inicia um novo jogo e retorna o ID do jogo"""
        if quantidade_jogadores < 2 or quantidade_jogadores > 10:
            raise ValueError("Número de jogadores deve ser entre 2 e 10")
        
        # Criar deck usando a fachada
        deck = CardFacade.create_uno_deck()
        deck = self._shuffle_deck(deck)
        
        # Criar jogadores
        players = []
        for i in range(quantidade_jogadores):
            players.append(Player(id=i))
        
        # Distribuir 5 cartas para cada jogador
        for player in players:
            for _ in range(5):
                if deck:
                    card = deck.pop()
                    player.add_card(card)
        
        # Colocar primeira carta na pilha de descarte
        discard_pile = []
        first_card = None
        while deck and (first_card is None or first_card.type != CardType.NUMBER):
            first_card = deck.pop()
            if first_card.type == CardType.NUMBER:
                discard_pile.append(first_card)
            else:
                deck.insert(0, first_card)  # Coloca no fundo do deck
                first_card = None
                
        if not discard_pile and deck:
            first_card = deck.pop()
            discard_pile.append(first_card)
        
        # Criar estado do jogo
        game_state = GameState(
            id=self.next_game_id,
            players=players,
            deck=deck,
            discard_pile=discard_pile,
            current_player_index=0,
            status=GameStatus.IN_PROGRESS,
            play_direction=PlayDirection.CLOCKWISE,
            current_color=discard_pile[0].color if discard_pile else None
        )
        
        self.games[self.next_game_id] = game_state
        game_id = self.next_game_id
        self.next_game_id += 1

        self.notify(game_state)
        
        return game_id
    
    def get_player_hand(self, game_id: int, player_id: int) -> List[Card]:
        """Retorna as cartas na mão do jogador"""
        game = self.games.get(game_id)
        if not game:
            raise ValueError("Jogo não encontrado")
        
        if player_id < 0 or player_id >= len(game.players):
            raise ValueError("Jogador não encontrado")
        
        return game.players[player_id].hand
       
    def get_current_player(self, game_id: int) -> int:
        """Retorna o ID do jogador da vez"""
        game = self.games.get(game_id)
        if not game:
            raise ValueError("Jogo não encontrado")
        
        return game.current_player_index
    
    def can_play_card(self, card: Card, top_card: Card, current_color: CardColor = None) -> bool:
        """Verifica se uma carta pode ser jogada sobre a carta do topo"""
        # Usar a fachada que considera a current_color
        return CardFacade.can_play_card(card, top_card, current_color)
    
    def get_playable_cards(self, game_id: int, player_id: int) -> List[Card]:
        """Retorna as cartas jogáveis do jogador"""
        game = self.games.get(game_id)
        if not game:
            raise ValueError("Jogo não encontrado")
        
        if player_id < 0 or player_id >= len(game.players):
            raise ValueError("Jogador não encontrado")
        
        top_card = game.get_top_discard_card()
        if not top_card:
            return []
        
        player_hand = game.players[player_id].hand
        return CardFacade.filter_playable_cards(player_hand, top_card)
    
    def jogar_carta(self, game_id: int, player_id: int, card_index: int, chosen_color: CardColor = None) -> dict:
        """Joga uma carta da mão do jogador"""
        game = self.games.get(game_id)
        if not game:
            raise ValueError("Jogo não encontrado")
        
        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Jogo não está em andamento")
        
        if player_id != game.current_player_index:
            raise ValueError("Não é a vez deste jogador")
        
        player = game.players[player_id]
        top_card = game.get_top_discard_card()
        
        if not top_card:
            raise ValueError("Não há carta no topo da pilha de descarte")
        
        if card_index < 0 or card_index >= len(player.hand):
            raise ValueError("Índice de carta inválido")
        
        card_to_play = player.hand[card_index]
        
        # Verificar se a carta pode ser jogada
        if not self.can_play_card(card_to_play, top_card, game.current_color):
            current_color_display = game.current_color.value if game.current_color else top_card.color.value
            raise ValueError(
            f"Carta não pode ser jogada. Carta do topo: {top_card}, "
            f"Cor atual: {current_color_display}"
        )
        
        # Validação para cartas curinga
        if card_to_play.type in [CardType.WILD, CardType.WILD_DRAW_FOUR] and not chosen_color:
            raise ValueError("Cartas curinga requerem uma cor escolhida. Use o parâmetro cor_escolhida.")
        
        # Validação da cor escolhida
        if chosen_color and chosen_color not in [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]:
            raise ValueError("Cor escolhida deve ser RED, BLUE, GREEN ou YELLOW")
        
        # Remover carta da mão do jogador e colocar na pilha de descarte
        played_card = player.remove_card(card_index)
        game.discard_pile.append(played_card)
        
        # Aplicar efeito da carta - passando a cor escolhida
        effect_result = game.apply_card_effect(played_card, chosen_color)
        
        # Atualizar cor atual se necessário
        if played_card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR] and chosen_color:
            game.current_color = chosen_color
        elif played_card.type != CardType.WILD and played_card.type != CardType.WILD_DRAW_FOUR:
            game.current_color = played_card.color
        
        # Verificar se o jogador ganhou
        if not player.has_cards():
            game.status = GameStatus.FINISHED
            game.winner = player_id
            game.next_turn()

            self.notify(game)

            return {
                "message": "Carta jogada com sucesso",
                "winner": player_id,
                "game_finished": True,
                "played_card": CardFacade.get_card_display_name(played_card),
                "effect": effect_result
            }

        game.next_turn()
        self.notify(game)
        
        return {
            "message": "Carta jogada com sucesso",
            "played_card": str(played_card),
            "next_player": game.current_player_index,
            "effect": effect_result
        }
    
    def passar_vez(self, game_id: int, player_id: int) -> dict:
        """Passa a vez, comprando uma carta"""
        game = self.games.get(game_id)
        if not game:
            raise ValueError("Jogo não encontrado")
        
        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Jogo não está em andamento")
        
        if player_id != game.current_player_index:
            raise ValueError("Não é a vez deste jogador")
        
        player = game.players[player_id]
        
        # Comprar uma carta do deck
        if game.deck:
            card = game.deck.pop()
            player.add_card(card)
            card_message = f"Comprou: {CardFacade.get_card_display_name(card)}"
        else:
            card_message = "Deck vazio - não foi possível comprar carta"
        
        # Passar para o próximo jogador
        game.next_turn()
        self.notify(game)
        
        return {
            "message": "Vez passada com sucesso",
            "card_bought": card_message,
            "next_player": game.current_player_index
        }
    
    def get_game_state(self, game_id: int) -> Optional[GameState]:
        """Retorna o estado completo do jogo (para debug)"""
        return self.games.get(game_id)


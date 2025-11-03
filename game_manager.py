import random
from typing import List, Dict, Optional
from models import Card, CardColor, CardType, Player, GameState, GameStatus

class GameManager:
    def __init__(self):
        self.games: Dict[int, GameState] = {}
        self.next_game_id = 1
    
    def _create_deck(self) -> List[Card]:
        """Cria um baralho completo de UNO (sem cartas especiais para esta versão)"""
        deck = []
        card_id = 0
        
        # Cartas numéricas (0-9) para cada cor
        for color in CardColor:
            # Uma carta 0 de cada cor
            deck.append(Card(id=card_id, color=color, type=CardType.NUMBER, value=0))
            card_id += 1
            
            # Duas cartas de 1-9 de cada cor
            for value in range(1, 10):
                deck.append(Card(id=card_id, color=color, type=CardType.NUMBER, value=value))
                card_id += 1
                deck.append(Card(id=card_id, color=color, type=CardType.NUMBER, value=value))
                card_id += 1
        
        return deck
    
    def _shuffle_deck(self, deck: List[Card]) -> List[Card]:
        """Embaralha o deck"""
        random.shuffle(deck)
        return deck
    
    def novo_jogo(self, quantidade_jogadores: int) -> int:
        """Inicia um novo jogo e retorna o ID do jogo"""
        if quantidade_jogadores < 2 or quantidade_jogadores > 10:
            raise ValueError("Número de jogadores deve ser entre 2 e 10")
        
        # Criar deck e embaralhar
        deck = self._create_deck()
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
        if deck:
            first_card = deck.pop()
            discard_pile.append(first_card)
        
        # Criar estado do jogo
        game_state = GameState(
            id=self.next_game_id,
            players=players,
            deck=deck,
            discard_pile=discard_pile,
            current_player_index=0,
            status=GameStatus.IN_PROGRESS
        )
        
        self.games[self.next_game_id] = game_state
        game_id = self.next_game_id
        self.next_game_id += 1
        
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
    
    def can_play_card(self, card: Card, top_card: Card) -> bool:
        """Verifica se uma carta pode ser jogada sobre a carta do topo"""
        # Cartas podem ser jogadas se forem da mesma cor ou mesmo valor
        return card.color == top_card.color or (
            card.type == CardType.NUMBER and 
            top_card.type == CardType.NUMBER and 
            card.value == top_card.value
        )
    
    def jogar_carta(self, game_id: int, player_id: int, card_index: int) -> dict:
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
        if not self.can_play_card(card_to_play, top_card):
            raise ValueError(f"Carta não pode ser jogada. Carta do topo: {top_card}")
        
        # Remover carta da mão do jogador e colocar na pilha de descarte
        played_card = player.remove_card(card_index)
        game.discard_pile.append(played_card)
        
        # Verificar se o jogador ganhou
        if not player.has_cards():
            game.status = GameStatus.FINISHED
            game.winner = player_id
            game.next_turn()
            return {
                "message": "Carta jogada com sucesso",
                "winner": player_id,
                "game_finished": True
            }
        
        # Passar para o próximo jogador
        game.next_turn()
        
        return {
            "message": "Carta jogada com sucesso",
            "played_card": str(played_card),
            "next_player": game.current_player_index
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
            card_message = f"Comprou: {card}"
        else:
            card_message = "Deck vazio - não foi possível comprar carta"
        
        # Passar para o próximo jogador
        game.next_turn()
        
        return {
            "message": "Vez passada com sucesso",
            "card_bought": card_message,
            "next_player": game.current_player_index
        }
    
    def get_game_state(self, game_id: int) -> Optional[GameState]:
        """Retorna o estado completo do jogo (para debug)"""
        return self.games.get(game_id)

# Instância global do gerenciador de jogos
game_manager = GameManager()
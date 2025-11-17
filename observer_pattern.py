from abc import ABC, abstractmethod
from typing import List, Any
from models import GameState  # Vamos importar o GameState para tipagem

# Interface para o Observador
class Observer(ABC):
    @abstractmethod
    def update(self, game_state: GameState):
        """Recebe a notificação do Subject."""
        pass

# Interface para o Sujeito (Subject)
class Subject(ABC):
    _observers: List[Observer] = []

    def attach(self, observer: Observer):
        """Adiciona um observador."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Remove um observador."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass # Ignora se o observador não estiver na lista

    @abstractmethod
    def notify(self, game_state: GameState):
        """Notifica todos os observadores sobre uma mudança."""
        for observer in self._observers:
            observer.update(game_state)
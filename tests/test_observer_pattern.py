import pytest
from unittest.mock import Mock
from observer_pattern import Subject, Observer
from models import GameState, GameStatus, Player, Card, CardColor, CardType
from card_facade import CardFacade


class ConcreteObserver(Observer):
    """Implementação concreta de Observer para testes"""
    def __init__(self):
        self.update_count = 0
        self.last_game_state = None
    
    def update(self, game_state: GameState):
        self.update_count += 1
        self.last_game_state = game_state


class ConcreteSubject(Subject):
    """Implementação concreta de Subject para testes"""
    def notify(self, game_state: GameState):
        """Notifica todos os observadores anexados."""
        for observer in self._observers:
            observer.update(game_state)


@pytest.fixture
def subject():
    """Cria uma instância de Subject para cada teste."""
    return ConcreteSubject()


@pytest.fixture
def observer():
    """Cria uma instância de Observer para cada teste."""
    return ConcreteObserver()


@pytest.fixture
def game_state():
    """Cria um GameState mock para os testes."""
    deck = CardFacade.create_uno_deck()
    players = [Player(id=0), Player(id=1)]
    
    return GameState(
        id=1,
        players=players,
        deck=deck,
        discard_pile=[],
        current_player_index=0,
        status=GameStatus.IN_PROGRESS
    )


def test_subject_initializes_empty_observers_list(subject):
    """Testa se o Subject inicializa com lista vazia de observadores."""
    assert len(subject._observers) == 0


def test_subject_attach_adds_observer(subject, observer):
    """Testa se attach adiciona um observador à lista."""
    subject.attach(observer)
    assert len(subject._observers) == 1
    assert observer in subject._observers


def test_subject_attach_prevents_duplicates(subject, observer):
    """Testa se attach não adiciona o mesmo observador duas vezes."""
    subject.attach(observer)
    subject.attach(observer)
    assert len(subject._observers) == 1


def test_subject_detach_removes_observer(subject, observer):
    """Testa se detach remove um observador da lista."""
    subject.attach(observer)
    subject.detach(observer)
    assert len(subject._observers) == 0
    assert observer not in subject._observers


def test_subject_detach_ignores_nonexistent_observer(subject, observer):
    """Testa se detach não falha ao tentar remover observador inexistente."""
    # Não deve lançar exceção
    subject.detach(observer)
    assert len(subject._observers) == 0


def test_subject_notify_calls_all_observers(subject, observer, game_state):
    """Testa se notify chama update em todos os observadores."""
    observer2 = ConcreteObserver()
    subject.attach(observer)
    subject.attach(observer2)
    
    subject.notify(game_state)
    
    assert observer.update_count == 1
    assert observer.last_game_state == game_state
    assert observer2.update_count == 1
    assert observer2.last_game_state == game_state


def test_subject_multiple_instances_have_separate_observers():
    """Testa se diferentes instâncias de Subject têm listas de observadores separadas."""
    subject1 = ConcreteSubject()
    subject2 = ConcreteSubject()
    observer1 = ConcreteObserver()
    observer2 = ConcreteObserver()
    
    subject1.attach(observer1)
    subject2.attach(observer2)
    
    assert len(subject1._observers) == 1
    assert len(subject2._observers) == 1
    assert observer1 in subject1._observers
    assert observer1 not in subject2._observers
    assert observer2 in subject2._observers
    assert observer2 not in subject1._observers


def test_observer_interface_requires_update_method():
    """Testa se Observer é uma classe abstrata que requer implementação de update."""
    with pytest.raises(TypeError):
        Observer()


def test_subject_interface_requires_notify_method():
    """Testa se Subject é uma classe abstrata que requer implementação de notify."""
    with pytest.raises(TypeError):
        Subject()


import actions
import strategy


class Player:
    def __init__(self, money=0, strategy=strategy.Pacifist(), player_id=None):
        self.money = money
        self.strategy = strategy
        self.id = player_id
        self.strategy.player = self

    def gain_money(self, amount) -> None:
        self.money += amount

    def lose_money(self, amount) -> None:
        self.money -= amount

    def act(self) -> actions.Action:
        return self.strategy.attack_choice()
import strategy
import actions
import player
import history
import random


class Game:
    def __init__(
            self,
            attack_cost=5,
            income_per_turn=2,
            starting_income=0,
            players=(),
            attack_delay=3
    ):
        self.attack_cost = attack_cost
        self.income_per_turn = income_per_turn
        self.id_to_player_dict = {}
        self.ledger = history.Ledger(set(players))
        self.starting_income = starting_income
        for current_player in self.ledger.living_players():
            current_player.money = starting_income
        self.pending_actions = []
        self.attack_delay = attack_delay
        self.index_id_to_player()
        self.inform_strategies()

    def perform_action(self, action):
        match action.action:
            case "attack":
                self.destroy_player(action.target)

    def delayed_action_ticks(self):
        for act in self.pending_actions:
            if act.next_round():
                self.perform_action(act)
                self.pending_actions.remove(act)

    def next_round(self) -> None:
        for current_player in self.ledger.living_players():
            current_player.gain_money(self.income_per_turn)
        self.ledger.next_round()
        self.delayed_action_ticks()

    def index_id_to_player(self) -> None:
        self.id_to_player_dict = {}
        for current_player in self.ledger.living_players():
            self.id_to_player_dict[current_player.id] = current_player

    def id_to_player(self, player_id) -> player.Player:
        return self.id_to_player_dict[player_id]

    def attack(self, attacker, target):
        if attacker.money >= self.attack_cost:
            attacker.money -= self.attack_cost
            if self.attack_delay == 0:
                self.destroy_player(target)
            else:
                self.pending_actions.append(actions.DelayedAction("attack", attacker, self.attack_delay, target=target))
            self.ledger.log_action('attack', attacker, target)

    def destroy_player(self, target):
        self.ledger.remove_player(target)
        if target.id in self.id_to_player_dict.keys():
            del self.id_to_player_dict[target.id]

    def steal(self, actor, target):
        if target.money >= 2:
            target.money -= 2
            actor.money += 2
            self.ledger.log_action('steal', actor, target)
        elif target.money > 0:
            actor.money += target.money
            target.money = 0
            self.ledger.log_action('steal', actor, target)

    def take_player_action(self, active_player):
        action = active_player.act()
        if action:
            match action.action:
                case "attack":
                    self.attack(action.actor, action.target)

    def do_round(self):
        for current_player in self.ledger.living_players():
            self.take_player_action(current_player)

    def inform_strategies(self):
        for current_player in self.ledger.living_players():
            current_player.strategy.ledger = self.ledger

    @classmethod
    def from_strat_list(
            cls,
            strat_list: list[strategy.Strategy],
            attack_cost=5,
            income_per_turn=2,
            starting_income=0,
            attack_delay=3
    ) -> "Game":
        players = [
            player.Player(starting_income, strat, id_num)
            for id_num, strat in enumerate(strat_list)
        ]
        game = cls(attack_cost, income_per_turn, starting_income, players, attack_delay)
        return game

    @classmethod
    def from_random_weights(
            cls,
            bias_range,
            was_attacked_range,
            money_diff_range,
            threshold_range,
            number_of_strats,
            attack_cost=5,
            income_per_turn=2,
            starting_income =0,
            attack_delay=3
    ) -> "Game":
        strategy_list = []
        for i in range(number_of_strats):
            strategy_list.append(strategy.WeightedStrategy(
                bias=random.uniform(bias_range[0], bias_range[1]),
                was_attacked=random.uniform(was_attacked_range[0], was_attacked_range[1]),
                money_difference=random.uniform(money_diff_range[0], money_diff_range[1]),
                threshold=random.uniform(threshold_range[0], threshold_range[1])
            ))
        return Game.from_strat_list(strategy_list, attack_cost, income_per_turn, starting_income, attack_delay)

    @classmethod
    def from_doubled_population(
            cls,
            strat_list: list[strategy.WeightedStrategy],
            entropy,
            attack_cost=5,
            income_per_turn=2,
            starting_income=0,
            attack_delay=3
    ) -> "Game":
        mutated_copies = [strat.mutate(entropy) for strat in strat_list]
        doubled_strat_list = list(strat_list) + mutated_copies
        return Game.from_strat_list(
            doubled_strat_list, attack_cost, income_per_turn, starting_income, attack_delay
        )

    def simulate_n_rounds(self, n: int) -> None:
        for i in range(n):
            self.do_round()
            self.next_round()

    def __str__(self) -> str:
        # noinspection PyListCreation
        lines_lst = [
            "=== GAME STATE ===",
            f"Settings: ",
            f"  Attack Cost={self.attack_cost}",
            f"  Income/Turn={self.income_per_turn}",
            f"  Attack Delay={self.attack_delay}",
            f"  Round: {self.ledger.round}",
            "------------------"
        ]

        lines_lst.append("Living Players:")
        living = list(self.ledger.living_players())
        if living:
            for current_player in living:
                strat_name = current_player.strategy
                lines_lst.append(f"  - [ID {current_player.id}] Strat: {strat_name} | Money: {current_player.money}") # noqa
        else:
            lines_lst.append("  - None (All players eliminated!)")

        lines_lst.append("==================")
        return "\n".join(lines_lst)

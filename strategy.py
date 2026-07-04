import random
import actions


class Strategy:
    def __init__(self, ledger=None, player=None):
        self.ledger = ledger
        self.player = player

    def attack_choice(self):
        return None

    def target_to_attack_intent(self, target):
        return actions.Action(action="attack", actor=self.player, target=target)


class WeightedStrategy(Strategy):
    def __init__(self, ledger=None, player=None, bias=1, was_attacked=1, money_difference=0, threshold=2):
        super().__init__(ledger, player)
        self.bias = bias
        self.was_attacked = was_attacked
        self.money_difference = money_difference
        self.threshold = threshold

    def player_score_to_attack(self, target):
        past_attacks_score = self.was_attacked * self.ledger.has_been_attacked_by(target, self.player)
        money_difference_score = self.money_difference * (target.money - self.player.money)
        return self.bias + (past_attacks_score + money_difference_score)

    def attack_choice(self):
        top_pick = (None, self.threshold)
        players = self.ledger.living_players().remove(self.player)
        for target_option in players:
            score = self.player_score_to_attack(target_option)
            if score >= top_pick[1]:
                top_pick = (target_option, score)
        if top_pick[0]:
            return self.target_to_attack_intent(top_pick[0])
        else:
            return None

    def to_dict(self):
        return {
            "bias": self.bias,
            "was_attacked": self.was_attacked,
            "money_difference": self.money_difference,
            "threshold": self.threshold,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            bias=data["bias"],
            was_attacked=data["was_attacked"],
            money_difference=data["money_difference"],
            threshold=data["threshold"],
        )

    def mutate(self, entropy):
        """
        Return a new WeightedStrategy with the same weights as this one,
        except each weight is nudged by a random amount in
        [-entropy, entropy]. `self` is left unchanged.
        """
        return WeightedStrategy(
            bias=self.bias + random.uniform(-entropy, entropy),
            was_attacked=self.was_attacked + random.uniform(-entropy, entropy),
            money_difference=self.money_difference + random.uniform(-entropy, entropy),
            threshold=self.threshold + random.uniform(-entropy, entropy),
        )


class Pacifist(Strategy):
    """Never attacks, no matter what. Useful as a baseline control group."""

    def attack_choice(self):
        return None


class Defensive(Strategy):
    def attack_choice(self):
        actions_history = self.ledger.past_actions
        for round_list in actions_history.values():
            for action in round_list:
                if (action.action == 'attack'
                        and action.actor in self.ledger.players
                        and not(self.ledger.has_been_attacked(action.actor))):
                    return actions.Action(action="attack", actor=self.player, target=action.actor)
        return None


class TitForTat(Strategy):
    """
    Only retaliates against whoever attacked *this player specifically*,
    and only looks at the most recent round of actions. Classic
    game-theory strategy: cooperate by default, mirror the last move
    made against you.
    """

    def attack_choice(self):
        if not self.ledger.past_actions:
            return None
        last_round_num = max(self.ledger.past_actions.keys())
        last_round_actions = self.ledger.past_actions[last_round_num]
        for action in last_round_actions:
            if (action.action == 'attack'
                    and action.target == self.player
                    and action.actor in self.ledger.players
                    and not (self.ledger.has_been_attacked(action.actor))):
                return actions.Action(action="attack", actor=self.player, target=action.actor)
        return None


class Vengeful(Strategy):
    """
    Like TitForTat, but never forgives: retaliates against *anyone* who
    has ever attacked this player, across the entire game history, as
    long as they're still alive. Grudges are permanent.
    """

    def attack_choice(self):
        for round_list in self.ledger.past_actions.values():
            for action in round_list:
                if (action.action == 'attack'
                        and action.target == self.player
                        and action.actor in self.ledger.players
                        and not (self.ledger.has_been_attacked(action.actor))):
                    return actions.Action(action="attack", actor=self.player, target=action.actor)
        return None


class RandomAttacker(Strategy):
    """
    Attacks a random living opponent with some fixed probability each
    round, regardless of history. A useful "noise" baseline to compare
    smarter strategies against.
    """

    def __init__(self, ledger=None, player=None, attack_probability=0.3):
        super().__init__(ledger, player)
        self.attack_probability = attack_probability

    def attack_choice(self):
        if random.random() > self.attack_probability:
            return None
        possible_targets = [p for p in self.ledger.players if p != self.player]
        if not possible_targets:
            return None
        target = random.choice(possible_targets)
        return actions.Action(action="attack", actor=self.player, target=target)


class AlwaysAttacker(Strategy):
    """
    The 'first strike' strategy: always attacks a random living
    opponent every round, no provocation needed. Good stress test for
    how forgiving/defensive strategies hold up under constant pressure.
    """

    def attack_choice(self):
        possible_targets = [
            p for p in self.ledger.players if p != self.player and not(self.ledger.has_been_attacked(p))
        ]
        if not possible_targets:
            return None
        target = random.choice(possible_targets)
        return actions.Action(action="attack", actor=self.player, target=target)

import actions


class Ledger(object):
    def __init__(self, players):
        self.round = 1
        self.past_actions = {
            1:[]
        }
        self.sequence_num = 0
        self.players = players
        self.dead_players = []
        self.death_round = {}

    def next_round(self):
        self.round += 1
        self.past_actions[self.round] = []

    def living_players(self):
        return self.players

    def remove_player(self, target_player):
        if target_player in self.players:
            self.players.remove(target_player)
            self.dead_players.append(target_player)
            self.death_round[target_player] = self.round

    def log_action(self, action_name, actor, target=None) -> None:
        self.sequence_num += 1

        new_action = actions.Action(
            action=action_name,
            actor=actor,
            round_done=self.round,
            sequence_number=self.sequence_num,
            target=target
        )
        self.past_actions[self.round].append(new_action)

    def has_been_attacked(self, target, since_round=None) -> bool:
        for round_num, round_actions in self.past_actions.items():
            if since_round is not None and round_num < since_round:
                continue
            for action in round_actions:
                if action.action == 'attack' and action.target == target:
                    return True
        return False

    def has_been_attacked_by(self, attacker, target, since_round=None):
        for round_num, round_actions in self.past_actions.items():
            if since_round is not None and round_num < since_round:
                continue
            for action in round_actions:
                if action.action == 'attack' and action.target == target and action.actor == attacker:
                    return True
        return False

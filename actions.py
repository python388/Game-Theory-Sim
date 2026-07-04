class Action:
    def __init__(self, action, actor, round_done=None, sequence_number=None, target=None):
        self.action = action
        self.actor = actor
        self.round = round_done
        self.sequence_num = sequence_number
        self.target = target

    def __str__(self) -> str:
        if self.target is None:
            return (
                f"Player ID: {self.actor}\n"
                f"did action {self.action}\n"
                f"on round {self.round}\n"
                f"with sequence number {self.sequence_num}"
            )
        else:
            return (
                f"Player ID: {self.actor}\n"
                f"did action {self.action}\n"
                f"to player {self.target}\n"
                f"on round {self.round}\n"
                f"with sequence number {self.sequence_num}"
            )


class DelayedAction(Action):
    def __init__(self, action, actor, delay, round_done=None, sequence_number=None, target=None):
        super().__init__(action, actor, delay, sequence_number, target)
        self.delay = delay

    def next_round(self):
        self.delay -= 1
        if self.delay <= 0:
            return True
        else:
            return False

    @classmethod
    def from_action(cls, action, delay):
        return cls(action.action, action.actor, delay, target=action.target)
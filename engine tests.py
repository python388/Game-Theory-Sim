import unittest
import engine
import player
import actions
import strategy


class MyTestCase(unittest.TestCase):
    def setup(self):
        self.test_game = engine.Game(
            income_per_turn=5,
            starting_income=0,
            players=[player.Player(player_id=1), player.Player(player_id=2)])

    def test_income(self):
        self.setup()
        self.assertEqual(self.test_game.id_to_player(1).money, 0)
        self.assertEqual(self.test_game.id_to_player(2).money, 0)
        self.test_game.next_round()
        self.assertEqual(self.test_game.id_to_player(1).money, 5)
        self.assertEqual(self.test_game.id_to_player(2).money, 5)

    def test_delayed_attack(self):
        self.setup()
        self.test_game.pending_actions.append(actions.DelayedAction(
            "attack",
            self.test_game.id_to_player(1),
            delay = 2,
            target=self.test_game.id_to_player(2)
        ))
        self.assertTrue(self.test_game.id_to_player(2) in self.test_game.ledger.living_players())
        self.test_game.next_round()
        self.assertTrue(self.test_game.id_to_player(2) in self.test_game.ledger.living_players())
        self.test_game.next_round()
        self.assertTrue(2 not in self.test_game.id_to_player_dict.keys())

    def test_weighted_strats(self):
        self.test_game = engine.Game(
            income_per_turn=5,
            starting_income=0,
            players=[
                player.Player(player_id=1, strategy=strategy.WeightedStrategy(was_attacked=3)),
                player.Player(player_id=2, strategy=strategy.WeightedStrategy(money_difference=1))
            ]
        )
        self.test_game.simulate_n_rounds(4)
        self.assertEqual(len(self.test_game.ledger.players), 2)
        self.test_game.ledger.log_action("attack", self.test_game.id_to_player(2), self.test_game.id_to_player(1))
        self.test_game.simulate_n_rounds(5)
        self.assertEqual(len(self.test_game.ledger.players), 1)
        self.test_game = engine.Game(
            income_per_turn=5,
            starting_income=5,
            players=[
                player.Player(player_id=1, strategy=strategy.WeightedStrategy(was_attacked=0)),
                player.Player(player_id=2, strategy=strategy.WeightedStrategy(money_difference=1))
            ]
        )
        self.test_game.id_to_player(1).money += 5
        self.test_game.simulate_n_rounds(5)
        self.assertEqual(len(self.test_game.ledger.players), 1)


if __name__ == '__main__':
    unittest.main()

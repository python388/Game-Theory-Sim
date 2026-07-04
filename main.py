import engine
import strategy
import json
import generationtools

def save_generation(strategies, filename):
    data = [s.to_dict() for s in strategies]
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_generation(filename):
    with open(filename) as f:
        data = json.load(f)
    return [strategy.WeightedStrategy.from_dict(d) for d in data]

if __name__ == "__main__":
    strategy_list = load_generation("gentest.json")
    game = engine.Game.from_doubled_population(strategy_list, 0.1)
    game.simulate_n_rounds(20)
    print(game)
    fittest_half = generationtools.calculate_fittest_half(game.ledger)
    print(fittest_half)
    save_generation(fittest_half, 'gentest.json')
    """game = engine.Game.from_strat_list(
        [strategy.RandomAttacker(), strategy.Pacifist(), strategy.Defensive(), strategy.Defensive()]
    )
    game.simulate_n_rounds(20)
    print(game)"""

import json

def calculate_fitness(ledger, player):
    if player in ledger.death_round.keys():
        return 100 * ledger.death_round[player] + player.money
    else:
        return 100 * ledger.round + player.money

def calculate_fittest_half(ledger):
    fitness_list = [(player, calculate_fitness(ledger, player)) for player in list(ledger.players) + ledger.dead_players]
    fitness_list.sort(key=lambda x: x[1])
    return list(map(lambda x: x[0].strategy, fitness_list[len(fitness_list)//2:]))
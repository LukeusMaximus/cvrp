import sys
import math
from random import shuffle, uniform, randint, choice
import pickle
import time

from distances import distances
from capacities import capacities

def find_in_list(l, x):
    if not (x in l):
        return -1
    for i in xrange(len(l)):
        if x == l[i]:
            return i
    return -1    
    
class cvrp_solver:
    def __init__(self, pop):
        self.dimension = 76
        self.depot_id = 1
        self.capacity = 220
        self.mutate_rate = 1
        self.population_size = pop
        self.generation = 0
        # Initialise the population
        genes = [x for x in xrange(2, self.dimension+1)]
        self.population = []
        for i in xrange(self.population_size):
            shuffle(genes)
            dna = list(genes)
            self.population.append((dna, self.__assess_fitness(dna)))
        self.population = sorted(self.population, key=lambda x : x[1])
        
    def __assess_fitness(self, genome):
        cost = distances[self.depot_id][genome[0]]
        delivered = capacities[genome[0]]
        for i in xrange(len(genome)-1):
            if delivered + capacities[genome[i+1]] > self.capacity:
                cost += distances[genome[i]][self.depot_id]
                cost += distances[self.depot_id][genome[i+1]]
                delivered = capacities[genome[i+1]]
            else:
                cost += distances[genome[i]][genome[i+1]]
                delivered += capacities[genome[i+1]]
        cost += distances[genome[-1]][self.depot_id]
        return cost
        
    def __choose_random_parent(self):
        weights = [0] * len(self.population)
        for i in xrange(len(self.population)):
            weights[i] = 1/self.population[i][1]
        a = uniform(0, sum(weights))
        j = 0
        while a > weights[j]: 
            a -= weights[j]
            j += 1
        return self.population[j]
        
    def __reproduce_crossover(self, p1_genome, p2_genome):
        # Produces an offspring using crossover
        a = randint(0, len(p1_genome)-1)
        b = randint(0, len(p1_genome)-1)
        while a == b:
            b = randint(0, len(p1_genome))
        if a > b:
            a,b = b,a
        pre_result = p1_genome[:a] + p2_genome[a:b] + p1_genome[a:]
        result = []
        for i in xrange(len(pre_result)):
            if not (pre_result[i] in result):
                result.append(pre_result[i])
        return result
        
    def __reproduce_mutation(self, genome):
        # Produces an offspring using mutation
        result = list(genome)
        gene = result.pop(randint(0, len(genome)-1))
        result.insert(randint(0, len(genome)-1), gene)
        return result
        
    def evolve(self):
        new_population = []
        
        # Crossover
        for i in xrange(self.population_size):
            # Select parents via proportional roulette
            parent1 = self.__choose_random_parent()
            parent2 = self.__choose_random_parent()
            while parent2 == parent1:
                # Ensure no asexual breeding
                parent2 = self.__choose_random_parent()
            child_dna = self.__reproduce_crossover(parent1[0], parent2[0])
            new_population.append((child_dna, self.__assess_fitness(child_dna)))
            
        # Mutate
        for i in xrange(self.mutate_rate):
            child_dna = self.__reproduce_mutation(choice(new_population)[0])
            new_population.append((child_dna, self.__assess_fitness(child_dna)))
            
        # Add children to the old population and assess their fitness
        new_population += self.population
        
        # Mutate recurrences
        self.population = []
        for x in new_population:
            if x in self.population:
                chid_dna = self.__reproduce_mutation(x[0])
                self.population.append((chid_dna, self.__assess_fitness(chid_dna)))
            else:
                self.population.append(x)
        
        # Cull the population in survival of the fittest        
        self.population = sorted(self.population, key=lambda x : x[1])[:self.population_size]
        self.generation += 1
    
    def print_poplation(self):
        for x in self.population:
            print x

    def print_stats(self):
        # Assumes the population is sorted
        best = self.population[0][1]
        worst = self.population[-1][1]
        val_range = worst - best
        print self.generation, best
        
    def print_best_to_file(self):
        genome = self.population[0][0]
        routes = []
        current_route = [1]
        delivered = 0
        for i in xrange(len(genome)):
            if delivered + capacities[genome[i]] > self.capacity:
                current_route.append(1)
                routes.append(current_route)
                current_route = [1]
                delivered = 0
            current_route.append(genome[i])
            delivered += capacities[genome[i]]
        current_route.append(1)
        routes.append(current_route)
        
        costs = [0] * len(routes)
        for i in xrange(len(routes)):
            cost = 0
            for j in xrange(len(routes[i])-1):
                cost += distances[routes[i][j]][routes[i][j+1]]
            costs[i] = cost
        assert abs(sum(costs) - self.population[0][1]) < 0.000001
        
        cost_str = str(sum(costs))
        dpp = cost_str.find(".")
        cost_str = cost_str[:dpp+4]
        best_file = open("solutions/best_sol_" + cost_str, "w")
        best_file.write("login lm9131\n")
        best_file.write("cost " + cost_str + "\n")
        for i in xrange(len(routes)): 
            s = ""
            for x in routes[i]:
                if s != "":
                    s += "->"
                s += str(x)
            best_file.write(s + "\n")
        best_file.close()
        
def normal_mode():
    start = time.time()
    solver = cvrp_solver(10)
    this_point = 0
    while this_point < 600:
        solver.evolve()
        if time.time()-start > this_point:
            print this_point, solver.population[0][1]
            this_point += 3
            solver.print_best_to_file()
    
def self_reboot_mode():
    while True:
        solver = cvrp_solver(10)
        best = solver.population[0][1]
        change_count = 0
        while change_count < 20:
            solver.evolve()
            if solver.generation % 100 == 0:
                solver.print_stats()
                solver.print_best_to_file()
                change_count += 1
                if solver.population[0][1] < best:
                    change_count = 0
                    best = solver.population[0][1]
        
if __name__ == "__main__":
    normal_mode()
    

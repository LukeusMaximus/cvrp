import sys
import math
from random import shuffle, uniform, randint, choice

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
    def __init__(self):
        self.dimension = 76
        self.depot_id = 1
        self.capacity = 220
        self.mutate_rate = 0.01
        self.best = None
        
    def __choose_random_parent(self):
        inverse_costs = {}
        for x in self.population:
            inverse_costs[x] = 1/self.population[x][1]
        total_fitnesses = sum([inverse_costs[x] for x in inverse_costs])
        a = uniform(0, total_fitnesses)
        j = 0
        keys = inverse_costs.keys()
        while a > inverse_costs[keys[j]]: 
            a -= inverse_costs[keys[j]]
            j += 1
        return self.population[keys[j]]
        
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
        if self.best == None or cost < self.best[1]:
            self.best = (genome, cost)
        return cost
        
    def __assess_population_fitness(self):
        for x in self.population:
            self.population[x] = (self.population[x][0], self.__assess_fitness(self.population[x][0]))
            
    def initialise_population(self, size):
        genes = [x for x in xrange(2, self.dimension+1)]
        self.population = []
        for i in xrange(size):
            shuffle(genes)
            dna = list(genes)
            self.population.append((dna, self.__assess_fitness(dna)))
        
    def evolve(self):
        new_population = {}
        
        # Crossover
        for i in xrange(len(self.population)):
            # Select parents via proportional roulette
            parent1 = self.__choose_random_parent()
            parent2 = self.__choose_random_parent()
            while parent2 == parent1:
                # Ensure no asexual breeding
                parent2 = self.__choose_random_parent()
            
            start_crossover_cycle = randint(0, len(parent1[0])-1)
            while parent1[0][start_crossover_cycle] == parent2[0][start_crossover_cycle]:
                # Make sure the crossover would actually change something
                start_crossover_cycle = randint(0, len(parent1[0])-1)
            
            # cyclic crossover for first direction
            child_dna = list(parent1[0])
            gene_buffer, child_dna[start_crossover_cycle] = child_dna[start_crossover_cycle], -1
            loc = find_in_list(parent2[0], gene_buffer)
            while child_dna[loc] != -1:
                child_dna[loc], gene_buffer = gene_buffer, child_dna[loc]
                loc = find_in_list(parent2[0], gene_buffer)
            child_dna[loc] = gene_buffer
            # DEBUG
            assert not (-1 in child_dna)
            for j in xrange(len(child_dna)):
                assert child_dna[j] == parent1[0][j] or child_dna[j] == parent2[0][j]
            # Add to new population
            new_population[i] = (child_dna, 0)
            
             # cyclic crossover for second direction
            child_dna = list(parent2[0])
            gene_buffer, child_dna[start_crossover_cycle] = child_dna[start_crossover_cycle], -1
            loc = find_in_list(parent1[0], gene_buffer)
            while child_dna[loc] != -1:
                child_dna[loc], gene_buffer = gene_buffer, child_dna[loc]
                loc = find_in_list(parent1[0], gene_buffer)
            child_dna[loc] = gene_buffer
            assert not (-1 in child_dna)
            for j in xrange(len(child_dna)):
                assert child_dna[j] == parent1[0][j] or child_dna[j] == parent2[0][j]
            new_population[i] = (child_dna, 0)
            
            
        # Mutate
        total_genes = sum([len(new_population[x][0]) for x in new_population])
        num_mutations = int(self.mutate_rate * total_genes)
        for i in xrange(num_mutations):
            # Select a random genome to mutate
            genome = list(new_population[choice(new_population.keys())][0])
            # Perform cyclic mutation
            gene = genome.pop(randint(0, len(genome)-1))
            genome.insert(randint(0, len(genome)-1), gene)
            new_population[i] = (child_dna, 0)

        # Replace old population and assess its fitness            
        self.population = new_population
        self.__assess_population_fitness()
    
    def print_poplation():
        for x in self.population:
            print self.population[x]

if __name__ == "__main__":
    solver = cvrp_solver()
    solver.initialise_population(10)
    for i in xrange(1):
        solver.evolve()
        print solver.best[1]
    print solver.best
    

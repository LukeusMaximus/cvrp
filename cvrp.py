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
    def __init__(self, pop):
        self.dimension = 76
        self.depot_id = 1
        self.capacity = 220
        self.mutate_rate = 0.01
        self.best = None
        self.population_size = pop
        self.__initialise_population()
        
    def __choose_random_parent(self):
        inverse_costs = [0] * len(self.population)
        for i in xrange(len(self.population)):
            inverse_costs[i] = 1/self.population[i][1]
        a = uniform(0, sum(inverse_costs))
        j = 0
        while a > inverse_costs[j]: 
            a -= inverse_costs[j]
            j += 1
        return self.population[j]
        
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
        for i in xrange(len(self.population)):
            self.population[i] = (self.population[i][0], self.__assess_fitness(self.population[i][0]))
            
    def __initialise_population(self):
        genes = [x for x in xrange(2, self.dimension+1)]
        self.population = []
        for i in xrange(self.population_size):
            shuffle(genes)
            dna = list(genes)
            self.population.append((dna, self.__assess_fitness(dna)))
        
    def evolve(self):
        new_population = []
        
        # Crossover
        for i in xrange(len(self.population)):
            # Select parents via proportional roulette
            parent1 = self.population[i]
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
            # If we already have this genome in the population...
            if child_dna in [x[0] for x in self.population + new_population]:
                # The child is dunked in radioactive waste and has its genes shuffled
                shuffle(child_dna)
            # Add it to the population
            new_population.append((child_dna, self.__assess_fitness(child_dna)))
            
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
            if child_dna in [x[0] for x in self.population + new_population]:
                shuffle(child_dna)
            new_population.append((child_dna, self.__assess_fitness(child_dna)))
            
            
        # Mutate
        total_genes = sum([len(x[0]) for x in new_population])
        num_mutations = int(self.mutate_rate * total_genes)
        for i in xrange(num_mutations):
            # Select a random genome to mutate
            genome = list(choice(new_population)[0])
            # Perform cyclic mutation
            gene = genome.pop(randint(0, len(genome)-1))
            genome.insert(randint(0, len(genome)-1), gene)
            new_population.append((genome, self.__assess_fitness(genome)))

        #print "\nold"
        #print [x[1] for x in self.population]
        #print "new"
        #print [x[1] for x in new_population]
        # Add children to the old population and assess their fitness        
        self.population += new_population
        # Cull the population in survival of the fittest        
        self.population = sorted(self.population, key=lambda x : x[1])[:self.population_size]
    
    def print_poplation(self):
        for x in self.population:
            print x

    def print_stats(self):
        # Assumes the population is sorted
        best = self.population[0][1]
        worst = self.population[-1][1]
        mean = sum([x[1] for x in self.population]) / len(self.population)
        val_range = worst - best
        median = self.population[(len(self.population)/2)-1][1]
        print "best:", best, "worst:", worst, "range:", val_range, "mean:", mean, "median:", median

if __name__ == "__main__":
    solver = cvrp_solver(10)
    for i in xrange(1000):
        solver.evolve()
        if i % 10 == 0:
            solver.print_stats()
    print solver.best
    

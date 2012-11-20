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
        self.mutate_rate = 0.0001
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
        return cost
        
    def evolve(self):
        new_population = []
        
        # Crossover
        for i in xrange(len(self.population)):
            # Select parents via proportional roulette
            parent1 = self.__choose_random_parent()
            parent2 = self.__choose_random_parent()
            while parent2 == parent1:
                # Ensure no asexual breeding
                parent2 = self.__choose_random_parent()
            
            start_crossover_cycle = randint(0, len(parent1[0])-1)
            '''
            while parent1[0][start_crossover_cycle] == parent2[0][start_crossover_cycle]:
                # Make sure the crossover would actually change something
                start_crossover_cycle = randint(0, len(parent1[0])-1)
            '''
            
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
            '''
            # If we already have this genome in the population...
            if child_dna in [x[0] for x in self.population + new_population]:
                # The child is dunked in radioactive waste and has its genes shuffled
                shuffle(child_dna)
            '''
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
            '''
            if child_dna in [x[0] for x in self.population + new_population]:
                shuffle(child_dna)
            '''
            new_population.append((child_dna, self.__assess_fitness(child_dna)))
            
        # Mutate
        total_genes = sum([len(x[0]) for x in new_population])
        fitness_range = self.population[-1][1] - self.population[0][1]
        if fitness_range == 0:
            fitness_range = 1
        diversity_reinvigorator = self.population[0][1] / fitness_range
        num_mutations = int(self.mutate_rate * total_genes * diversity_reinvigorator)
        for i in xrange(num_mutations):
            # Select a random genome to mutate
            genome = list(choice(new_population)[0])
            # Perform cyclic mutation
            gene = genome.pop(randint(0, len(genome)-1))
            genome.insert(randint(0, len(genome)-1), gene)
            new_population.append((genome, self.__assess_fitness(genome)))
            
        #if self.generation % 10 == 0:
            #print "\nold"
            #print [x[1] for x in self.population]
            #print "new"
            #print [x[1] for x in new_population]
        # Add children to the old population and assess their fitness
        #new_population.append(self.population[0])
        new_population += self.population
        
        # Mutate recurrences
        self.population = []
        for x in new_population:
            if x in self.population:
                genome = x[0]
                gene = genome.pop(randint(0, len(genome)-1))
                genome.insert(randint(0, len(genome)-1), gene)
                self.population.append((genome, self.__assess_fitness(genome)))
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
        print str(self.generation) + ":", "best:", best, "worst:", worst, "range:", val_range
        
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
    solver = cvrp_solver(10)
    for i in xrange(10000):
        solver.evolve()
        if solver.generation % 100 == 0:
            solver.print_stats()
            solver.print_best_to_file()
    print solver.population[0]
    solver.print_best_to_file()
        
def combo_mode():
    print "Start with multi solver"
    solvers = []
    for i in xrange(10):
        solvers.append(cvrp_solver(10))
    
    for i in xrange(1000):
        for x in solvers:
            x.evolve()
            if x.generation % 100 == 0:
                x.print_stats()
                x.print_best_to_file()
        if solvers[0].generation % 100 == 0:
            print ""
                
    print "Reduce to single solver"
    solver = cvrp_solver(10)
    solver.population = []
    for x in solvers:
        solver.population += x.population
    solver.population = sorted(solver.population, key=lambda x : x[1])
    
    for i in xrange(1000):
        solver.evolve()
        if solver.generation % 100 == 0:
            solver.print_stats()
            solver.print_best_to_file()
    print solver.population[0]
    solver.print_best_to_file()
        
def fold_mode():
    print "Start with folding solver"
    solvers = []
    for i in xrange(256):
        solvers.append(cvrp_solver(10))
    
    iteration_const = 512
    while len(solvers) > 1:
        iterations = iteration_const / len(solvers)
        for i in xrange(iterations):
            print i
            for x in solvers:
                x.evolve()
            if i == iterations - 1:
                for x in solvers:
                    x.print_stats()
                    x.print_best_to_file()
                print ""
        # Fold
        num_solvers = len(solvers) / 2
        if 2 * num_solvers < len(solvers):
            num_solvers += 1
        for i in xrange(num_solvers):
            if i + num_solvers < len(solvers):
                solvers[i].population += solvers[i + num_solvers].population
                solvers[i].population = sorted(solvers[i].population, key=lambda x : x[1])
        solvers = solvers[:num_solvers]
                
    solver = solvers[0]
    for i in xrange(1000):
        solver.evolve()
        if solver.generation % 100 == 0:
            solver.print_stats()
            solver.print_best_to_file()
    print solver.population[0]
    solver.print_best_to_file()
        
if __name__ == "__main__":
    normal_mode()
    

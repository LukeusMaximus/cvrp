import sys
import math
from random import shuffle, uniform, randint

def find_in_list(l, x):
    if not (x in l):
        return -1
    for i in xrange(len(l)):
        if x == l[i]:
            return i
    return -1    
    
class cvrp_solver:
    def __init__(self, nodes, depot_id, capacity):
        self.nodes = nodes
        self.dimension = len(nodes)
        self.depot_id = depot_id
        self.capacity = capacity
        self.mutate_rate = 0.01
        
    def __distance(self, id1, id2):
        return math.sqrt((self.nodes[id1][0] - self.nodes[id2][0])**2 + (self.nodes[id1][1] - self.nodes[id2][1])**2)
        
    def __choose_random_parent():
        total_fitnesses = sum([self.population[x][1] for x in self.population])
        a = uniform(0, total_fitnesses)
        j = 0
        while a > self.population[keys[j]][1]: 
            a -= self.population[keys[j]][1]
            j += 1
        return self.population[keys[j]]
        
    def __assess_fitness(genome):
        cost = self.__distance(depot_id, genome[0])
        delivered = self.nodes[genome[0]][2]
        for i in xrange(len(genome)-1):
            if delivered + self.nodes[genome[i+1]][2] > self.capacity:
                cost += self.__distance(genome[i], depot_id)
                cost += self.__distance(depot_id, genome[i+1])
                delivered = self.nodes[genome[i+1]][2]
            else:
                cost += self.__distance(genome[i], genome[i+1])
                delivered += self.nodes[genome[i+1]][2]
        cost += self.__distance(genome[-1], depot_id)
        return 1.0/cost
        
    def __assess_population_fitness():
        for x in self.population:
            self.population[x] = (self.population[x][0], __assess_fitness(self.population[x][0]))
            
    def initialise_population(self, size):
        genes = self.nodes.keys()
        genes.remove(depot_id)
        self.population = {}
        for i in xrange(size):
            shuffle(genes)
            dna = list(genes)
            self.population[i] = (dna, __assess_fitness(dna))
        __assess_poulation_fitness()
        
    def evlolve(self):
        new_population = {}
        
        # Crossover
        for i in xrange(len(self.population)):
            # Select parents via proportional roulette
            parent1 = __choose_random_parent()
            parent2 = __choose_random_parent()
            while parent2 == parent1:
                # Ensure no asexual breeding
                parent2 = __choose_random_parent()
            # cyclic crossover
            child_dna = list(parent1[0])
            start_crossover_cycle = randint(0, len(child_dna)-1)
            while child_dna[start_crossover_cycle] == parent2[0][start_crossover_cycle]:
                # Make sure the crossover would actually change something
                start_crossover_cycle = randint(0, len(child_dna)-1)
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
            
        # Mutate
        total_genes = sum([len(x[0]) for x in new_population])
        num_mutations = int(self.mutate_rate * total_genes)
        for i in xrange(num_mutations):
            # Select a random genome to mutate
            a = randint(0, len(new_population.keys()) - 1)
            genome = new_population[new_population.keys()[a]]
            # Perform cyclic mutation
            
        self.population = new_population
        __assess_population_fitness()

def parse_file(filename):
    cvrp_file = open(sys.argv[1])
    lines = cvrp_file.readlines()
    coord_sec = -1
    dem_sec = -1
    dep_sec = -1
    dimension = -1
    capacity = -1
    for i in xrange(len(lines)):
        if lines[i][:9] == "DIMENSION":
            dimension = int(lines[i][lines[i].find(":")+1:].strip())
        elif lines[i][:8] == "CAPACITY":
            capacity = int(lines[i][lines[i].find(":")+1:].strip())
        elif lines[i] == "NODE_COORD_SECTION\n":
            coord_sec = i
        elif lines[i] == "DEMAND_SECTION\n":
            dem_sec = i
        elif lines[i] == "DEPOT_SECTION\n":
            dep_sec = i
    if coord_sec == -1 or dem_sec == -1 or dep_sec == -1 or dimension == -1 or capacity == -1:
        raise Exception("Missing section")
    nodes = {}
    for i in xrange(1, dimension + 1):
        coord_line_vals = [int(x) for x in lines[coord_sec + i].split(" ")]
        dem_line_vals = [int(x) for x in lines[dem_sec + i].split(" ")]
        assert coord_line_vals[0] == dem_line_vals[0]
        nodes[coord_line_vals[0]] = (coord_line_vals[1], coord_line_vals[2], dem_line_vals[1])
    depot_id = int(lines[dep_sec+1])
    return nodes, depot_id, capacity

if __name__ == "__main__":
    if len(sys.argv) == 2:
        nodes, depot_id, capacity = parse_file(sys.argv[1])
        solver = cvrp_solver(nodes, depot_id, capacity)
        solver.initialise_population(10)
        solver.calculate_fitnesses()
        solver.crossover()
    else:
        print "Incorrcect number of arguments.\nUsage: \"python cvrp.py <vrp_file>\""


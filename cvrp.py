import sys
import math
from random import shuffle, uniform

class cvrp_solver:
    def __init__(self, nodes, depot_id, capacity):
        self.nodes = nodes
        self.dimension = len(nodes)
        self.depot_id = depot_id
        self.capacity = capacity
    def __distance(self, id1, id2):
        return math.sqrt((self.nodes[id1][0] - self.nodes[id2][0])**2 + (self.nodes[id1][1] - self.nodes[id2][1])**2)
    def initialise_population(self, size):
        genes = self.nodes.keys()
        genes.remove(depot_id)
        self.population = {}
        for i in xrange(size):
            shuffle(genes)
            self.population[i] = (list(genes), 0)
    def calculate_fitnesses(self):
        keys = self.population.keys()
        for x in keys:
            genome = self.population[x][0]
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
            self.population[x] = (genome, 1.0/cost)
        print [(x, self.population[x][1]) for x in self.population]
    def crossover(self):
        total_fitnesses = sum([self.population[x][1] for x in self.population])
        new_population = {}
        keys = self.population.keys()
        for i in xrange(len(self.population)):
            a = uniform(0, total_fitnesses)
            j = 0
            while a > self.population[keys[j]][1]: 
                a -= self.population[keys[j]][1]
                j += 1
            parent1 = self.population[keys[j]]
            a = uniform(0, total_fitnesses)
            j = 0
            while a > self.population[keys[j]][1]: 
                a -= self.population[keys[j]][1]
                j += 1
            parent2 = self.population[keys[j]]
            print parent1[1], parent2[1]
        
    def mutate(self):
        pass    

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


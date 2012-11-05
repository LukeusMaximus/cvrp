import sys
import math
from random import shuffle

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
            dna = genes
            shuffle(dna)
            self.population[i] = (dna, 0)
            print self.population[i]
    def calculate_fitnesses(self):
        for x in self.population.keys():
            genome = self.population[x][0]
            cap = self.capacity
            cost = self.__distance(depot_id, genome[0])
            cap -= self.nodes[genome[0]][2]
            previous_depot_visit = 0
            for i in xrange(len(genome)-1):
                if cap - self.nodes[genome[i+1]][2] < 0:
                    delivered = sum([nodes[x][2] for x in genome[previous_depot_visit:i+1]])
                    assert delivered < self.capacity
                    
                    cost += self.__distance(genome[i], depot_id)
                    cap = self.capacity
                    cost += self.__distance(depot_id, genome[i+1])
                    previous_depot_visit = i+1
                else:
                    cost += self.__distance(genome[i], genome[i+1])
                cap -= self.nodes[genome[i+1]][2]
            self.population[x] = genome, cost
        print self.population
    def crossover(self):
        #Also selects parents
        pass
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
        solver.initialise_population(1)
        solver.calculate_fitnesses()
    else:
        print "Incorrcect number of arguments.\nUsage: \"python cvrp.py <vrp_file>\""


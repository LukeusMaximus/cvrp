from distances import distances
from capacities import capacities
from random import shuffle, uniform, choice

class cGA_solver():
    def __init__(self):
        #general
        self.max_steps = 10000
        self.opt = 2
        self.lmb = 1
        self.dim = 75
        self.routes = 7
        
        #fitness
        self.capacity = 220
        self.overcap_weight = 10
        self.f_max = sum([sum([distances[x][y] for y in distances[x]]) for x in distances])
        
        #parent selection
        self.p = 0.3
        
        #toroidal cell grid
        self.width = 10
        self.height = 10
        self.cells = [[([],0) for i in xrange(self.height)] for j in xrange(self.width)]
        genes = range(2, self.dim + self.routes + 1)
        for x in xrange(self.width):
            for y in xrange(self.height):
                shuffle(genes)
                self.cells[x][y][0] = list(genes)
                self.cells[x][y][1] = self.__evaluate_fitness(self.cells[x][y][0])
                
    def __evaluate_fitenss(self, genome):
        cost = 0
        previous = 1
        over_cap = 0
        delivered = 0
        for i in xrange(len(genome)):
            if genome[i] > self.dim + 1:
                cost += distances[previous][1]
                previous = 1
                if delivered > self.capacity:
                    over_cap += delivered - self.capacity
                delivered = 0
            else:
                cost += distances[previous][genome[i]]
                previous = genome[i]
                delivered += capacities[genome[i]]
        cost += distances[previous][1]
        if delivered > self.capacity:
            over_cap += delivered - self.capacity
        delivered = 0
        return self.f_max - (cost + over_cap * self.overcap_weight)
    
    def __select_parents(self, x, y):
        candidates = [self.cells[x][y], self.cells[(x+1)%self.width][y], self.cells[x][(y+1)%self.height], self.cells[(x-1)%self.width][y], self.cells[x][(y-1)%self.height]]
        candidates = sorted(candidates, key=lambda x : x[1])
        candidates.reverse()
        selected = None
        i = 0
        while selected = None:
            if uniform(0,1) < self.p:
                selected = candidates[i]
            if i == len(candidates) - 1:
                i = 0
            else:
                i += 1
        return self.cells[x][y], selected
    
    def __crossover_parents(self, parents):
        genome1 = parents[0][0]
        genome2 = parents[1][0]
        adjacent = {1:[]}
        for x in genome1:
            adjacent[x] = []
        temp = [1] + genome1 + [1] + genome[2] + [1]
        for i in xrange(1,len(temp)-1):
            if not (temp[i+1] in adjacent[temp[i]])
                adjacent[temp[i]].append(temp[i+1])
            if not (temp[i-1] in adjacent[temp[i]])
                adjacent[temp[i]].append(temp[i-1])
        # Perhaps move edges from 77 - 82 into 1 here
        genome3 = [choice(genome1)]
        remaining = genome1
        remaining.remove(genome3[-1])
        for x in adjacent:
            adjacent[x].remove(genome3[0])
        while len(genome3) < len(genome1):
            if len(adjacent[genome3[-1]]) > 0:
                shortest = None
                shortest_len = self.dim + self.routes + 2
                for x in adjacent[genome3[-1]]:
                    if len(adjacent[x]) < shortest_len:
                        shortest = x
                        shortes_len = len(adjacent[x])
                assert shortest != None
                genome3.append(shortest)
                remaining.remove(genome3[-1])
            else:
                genome3.append(choice(remaining))
                remaining.remove(genome3[-1])
            for x in adjacent:
                adjacent[x].remove(genome3[-1])
            assert len(remaining) + len(genome3)
        return genome3
        
    
    def solve():
        for s in xrange(self.max_steps):
            for x in xrange(self.width):
                for y in xrange(self.height):
                    parents = self.__select_parents(x, y)
                    #aux indiv = Recombination(cga.Pc,parents);
                    #aux indiv = Mutation(cga.Pm,aux indiv);
                    #aux indiv = Local Search(cga.Pl,aux indiv);
                    #Evaluate Fitness(aux indiv);
                    #Insert If Better(position(x,y),aux indiv,cga,aux pop);
            #cga.pop = aux pop;
            #Update Statistics(cga);


if __name__ == "__main__":
    pass

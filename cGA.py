from distances import distances
from capacities import capacities
from random import shuffle, uniform, choice, randint

# Implements the algorithm described in
#
# Solving the Vehicle Routing Problem by Using Cellular Genetic Algorithms
#                                 by
#                    Enrique Alba and Bernab Dorronsoro

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
        self.overcap_weight = 1000
        self.f_max = 10**7
        
        #parent selection
        self.p = 0.3
        
        #mutation
        self.mutate_prob = 0.003
        
        #toroidal cell grid
        self.width = 10
        self.height = 10
        self.cells = [[([],0) for i in xrange(self.height)] for j in xrange(self.width)]
        genes = range(2, self.dim + self.routes + 1)
        for x in xrange(self.width):
            for y in xrange(self.height):
                shuffle(genes)
                genome = list(genes)
                self.cells[x][y] = (genome, self.__evaluate_fitness(genome))
                
    def __evaluate_fitness(self, genome):
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
        while selected == None:
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
        assert len(genome1) == self.dim + self.routes - 1
        assert len(genome2) == self.dim + self.routes - 1
        adjacent = {}
        for x in genome1:
            adjacent[x] = []
        for i in xrange(1,len(genome1)-1):
            if not (genome1[i+1] in adjacent[genome1[i]]):
                adjacent[genome1[i]].append(genome1[i+1])
            if not (genome1[i-1] in adjacent[genome1[i]]):
                adjacent[genome1[i]].append(genome1[i-1])
        for i in xrange(1,len(genome2)-1):
            if not (genome2[i+1] in adjacent[genome2[i]]):
                adjacent[genome2[i]].append(genome2[i+1])
            if not (genome2[i-1] in adjacent[genome2[i]]):
                adjacent[genome2[i]].append(genome2[i-1])
        genome3 = [choice(genome1)]
        remaining = list(genome1)
        remaining.remove(genome3[-1])
        for x in adjacent:
            if genome3[0] in adjacent[x]:
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
                if genome3[-1] in adjacent[x]:
                    adjacent[x].remove(genome3[-1])
            assert len(remaining) + len(genome3) == len(genome1)
        return genome3
        
    def __mutate_genome(self, genome):
        for i in xrange(0, len(genome)):
            if uniform(0, 1) < self.mutate_prob:
                op = randint(0, 2)
                r = randint(0, len(genome)-1)
                if op == 0:
                    #insert
                    genome.insert(r, genome.pop(i))
                elif op == 2:
                    #swap
                    genome[r], genome[i] = genome[i], genome[r]
                else:
                    #invert
                    a, b = i, r
                    if a > b:
                        a, b = b, a
                    cut = genome[a:b]
                    cut.reverse()
                    genome = genome[:a] + cut + genome[b:]
        return genome
    
    def __local_search(self, genome):
        #2-opt
        
        #lambda interchange
        diff_routes = False
        a = -1
        b = -1
        while not diff_routes:
            a = randint(0, len(genome) - 1)
            while a > self.dim + 1:
                a = randint(0, len(genome) - 1)
            b = randint(0, len(genome) - 1)
            while b > self.dim + 1:
                b = randint(0, len(genome) - 1)
            a, b = min(a,b), max(a,b)
            for i in xrange(a+1, b):
                if genome[i] > self.dim + 1:
                    diff_routes = True
        genome[a], genome[b] = genome[b], genome[a]
    
    def print_best_to_file(self, genome, fitness):
        routes = []
        current_route = [1]
        for i in xrange(len(genome)):
            if genome[i] > self.dim + 1:
                current_route.append(1)
                routes.append(current_route)
                current_route = [1]
            else:
                current_route.append(genome[i])
        current_route.append(1)
        routes.append(current_route)
        
        cost_str = str(fitness)
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
    
    def solve(self):
        best = None
        best_fitness = 0
        for s in xrange(self.max_steps):
            aux_pop = [[([],0) for i in xrange(self.height)] for j in xrange(self.width)]
            for x in xrange(self.width):
                for y in xrange(self.height):
                    parents = self.__select_parents(x, y)
                    aux_indiv = self.__crossover_parents(parents)
                    aux_indiv = self.__mutate_genome(aux_indiv)
                    #aux indiv = Local Search(cga.Pl,aux indiv);
                    fitness = self.__evaluate_fitness(aux_indiv)
                    if fitness > self.cells[x][y][1]:
                        aux_pop[x][y] = (aux_indiv, fitness)
                        if fitness > best_fitness:
                            best = aux_indiv
                            best_fitness = fitness
                    else:
                        aux_pop[x][y] = self.cells[x][y]
            self.cells = aux_pop;
            if s % 100 == 0:
                print best, best_fitness, self.f_max-best_fitness
                self.print_best_to_file(best, best_fitness)


if __name__ == "__main__":
    solver = cGA_solver()
    solver.solve()

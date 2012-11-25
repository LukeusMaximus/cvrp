from distances import distances
from capacities import capacities
from random import shuffle, uniform, choice, randint

# Implements the algorithm described in
#
# Solving the Vehicle Routing Problem by Using Cellular Genetic Algorithms
#                                 by
#                    Enrique Alba and Bernab Dorronsoro

class cGA_solver2():
    def __init__(self):
        #general
        self.max_steps = 2000
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
        genes = range(2, self.dim + 2)
        for x in xrange(self.width):
            for y in xrange(self.height):
                shuffle(genes)
                genome = list(genes)
                self.cells[x][y] = (genome, self.__evaluate_fitness(genome))
                
    def __evaluate_fitness(self, genome):
        cost = distances[1][genome[0]]
        delivered = capacities[genome[0]]
        for i in xrange(len(genome)-1):
            if delivered + capacities[genome[i+1]] > self.capacity:
                cost += distances[genome[i]][1]
                cost += distances[1][genome[i+1]]
                delivered = capacities[genome[i+1]]
            else:
                cost += distances[genome[i]][genome[i+1]]
                delivered += capacities[genome[i+1]]
        cost += distances[genome[-1]][1]
        return cost
    
    def __select_parents(self, x, y):
        candidates = [self.cells[x][y], self.cells[(x+1)%self.width][y], self.cells[x][(y+1)%self.height], self.cells[(x-1)%self.width][y], self.cells[x][(y-1)%self.height]]
        candidates = sorted(candidates, key=lambda x : x[1])
        selected = None
        i = 0
        while i < len(candidates) - 1:
            if uniform(0,1) < self.p:
                selected = candidates[i]
            i += 1
        if selected == None:
            selected = candidates[-1]
        return [self.cells[x][y], selected]
    
    def __crossover_parents(self, genome1, genome2):
        # Produces an offspring using crossover
        a = randint(0, len(genome1)-1)
        b = randint(0, len(genome1)-1)
        while a == b:
            b = randint(0, len(genome1))
        if a > b:
            a,b = b,a
        pre_result1 = genome1[:a] + genome2[a:b] + genome1[a:]
        pre_result2 = genome2[:a] + genome1[a:b] + genome2[a:]
        results = [[],[]]
        for i in xrange(len(pre_result1)):
            if not (pre_result1[i] in results[0]):
                results[0].append(pre_result1[i])
        for i in xrange(len(pre_result2)):
            if not (pre_result2[i] in results[1]):
                results[1].append(pre_result2[i])
        return results
        
    def __mutate_genome(self, genome):
        mutant = list(genome)
        for i in xrange(len(mutant)):
            if uniform(0, 1) < self.mutate_prob:
                op = randint(0, 2)
                r = randint(0, len(mutant)-1)
                if op == 0:
                    #insert
                    mutant.insert(r, mutant.pop(i))
                elif op == 2:
                    #swap
                    mutant[r], mutant[i] = mutant[i], mutant[r]
                else:
                    #invert
                    a, b = i, r
                    if a > b:
                        a, b = b, a
                    cut = mutant[a:b]
                    cut.reverse()
                    mutant = mutant[:a] + cut + mutant[b:]
        return mutant
    
    def __local_search(self, genome):
        #2-opt (a very shaky implementation given the representation)
        a = randint(2, len(genome) - 2)
        best = (None, self.__evaluate_fitness(genome))
        for i in xrange(len(genome)-a):
            test = list(genome)
            rev = test[i:i+a]
            rev.reverse()
            test = test[:i] + rev + test[i+a:]
            assert len(test) == len(genome)
            fitness = self.__evaluate_fitness(test)
            if fitness < best[1]:
                best = (test, fitness)
        return best[0]
        
        #lambda interchange
        '''
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
        '''
    
    def print_best_to_file(self, genome, fitness):
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
        assert abs(sum(costs) - fitness) < 0.000001
        
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
        best_fitness = -1
        for s in xrange(self.max_steps):
            aux_pop = [[([],0) for i in xrange(self.height)] for j in xrange(self.width)]
            for x in xrange(self.width):
                for y in xrange(self.height):
                    # Select
                    parents = self.__select_parents(x, y)
                    # Crossover
                    new_genomes = self.__crossover_parents(parents[0][0], parents[1][0])
                    # Mutate
                    mutant_genomes = []
                    for genome in new_genomes:
                        mutant_genomes.append(self.__mutate_genome(genome))
                    new_genomes += mutant_genomes
                    # Local Search
                    opt_genome = self.__local_search(choice(new_genomes));
                    if opt_genome != None:
                        new_genomes.append(opt_genome)
                    # Fitness Evaluation
                    trial_genomes = []
                    for genome in new_genomes:
                        trial_genomes.append((genome, self.__evaluate_fitness(genome)))
                    trial_best = sorted(trial_genomes, key = lambda x : x[1])[0]
                    if trial_best[1] < self.cells[x][y][1]:
                        aux_pop[x][y] = trial_best
                        if trial_best[1] < best_fitness or best == None:
                            best = trial_best[0]
                            best_fitness = trial_best[1]
                    else:
                        aux_pop[x][y] = self.cells[x][y]
            self.cells = aux_pop;
            if s % 100 == 0:
                print best_fitness
                self.print_best_to_file(best, best_fitness)


if __name__ == "__main__":
    for i in xrange(10):
        solver = cGA_solver2()
        solver.solve()

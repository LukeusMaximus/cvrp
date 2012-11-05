import sys

class node:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d

def parse_file(filename):
    cvrp_file = open(sys.argv[1])
    lines = cvrp_file.readlines()
    coord_sec = -1
    dem_sec = -1
    dep_sec = -1
    dimension = -1
    for i in xrange(len(lines)):
        if lines[i][:9] == "DIMENSION":
            dimension = int(lines[i][lines[i].find(":")+1:].strip())
        elif lines[i] == "NODE_COORD_SECTION\n":
            coord_sec = i
        elif lines[i] == "DEMAND_SECTION\n":
            dem_sec = i
        elif lines[i] == "DEPOT_SECTION\n":
            dep_sec = i
    print coord_sec, dem_sec, dep_sec, dimension
    if coord_sec == -1 or dem_sec == -1 or dep_sec == -1:
        raise Exception("Missing section")
    
    for i in xrange(dimension):
        
    

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_file(sys.argv[1])
    else:
        print "Incorrcect number of arguments.\nUsage \"python cvrp.py <vrp_file>\""


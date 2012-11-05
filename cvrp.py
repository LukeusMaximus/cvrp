import sys

class node:
    def __init__(self, ID, x, y, d):
        self.ID = ID
        self.x = x
        self.y = y
        self.d = d

#def ca

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
    print coord_sec, dem_sec, dep_sec, dimension, capacity
    if coord_sec == -1 or dem_sec == -1 or dep_sec == -1 or dimension == -1 or capacity == -1:
        raise Exception("Missing section")
    
    nodes = {}
    for i in xrange(1, dimension + 1):
        coord_line_vals = [int(x) for x in lines[coord_sec + i].split(" ")]
        dem_line_vals = [int(x) for x in lines[dem_sec + i].split(" ")]
        assert coord_line_vals[0] == dem_line_vals[0]
        nodes[coord_line_vals[0]] = node(coord_line_vals[0], coord_line_vals[1], coord_line_vals[2], dem_line_vals[1])
    
    depot_id = int(lines[dep_sec+1])
    
    return nodes, depot_id, capacity

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_file(sys.argv[1])
    else:
        print "Incorrcect number of arguments.\nUsage: \"python cvrp.py <vrp_file>\""


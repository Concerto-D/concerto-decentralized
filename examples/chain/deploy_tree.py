import sys
from mad import *

from node import Node

def get_name(i,j):
    return "n_" + str(i) + "_" + str(j)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("*** Error: missing parameters!\n")
        print("deploy.py <high of the tree> (starting to 0)\n")
        sys.exit(-1)
    else:
        height = int(sys.argv[1])
        if height < 0:
            print("*** Warning: at least of 1 level. 1 level will be used.\n")
            height = 0

        # Composant Provider
        ass = Assembly()
        nodes = {}

        client = Node(False, True) # only 1 use
        ass.addComponent("client", client)
        for i in range(height):
            for j in range(2**i):
                name = get_name(i,j)
                n = Node(i==height-1)
                nodes[name] = n
                ass.addComponent(name, n)
                print("new component: "+name)

        for i in range(height):
            for j in range(2**i):
                # Connecting the client to all
                name = get_name(i,j)
                print("name: "+name)
                n = nodes[name]                
                ass.addConnection(n, 'p', client, 'u')
                print("client connection: "+n.name+'.p <- '+ client.name+'.u')
                if i<height-1: # if not last line, connect to 2*j & 2j+1                    
                    n1=nodes[get_name(i+1, 2*j)]
                    n2=nodes[get_name(i+1, 2*j+1)]
                    print("   new connection: "+n1.name+'.p <- '+ n.name+'.u')
                    ass.addConnection(n1, 'p', n, 'u')
                    print("   new connection: "+n1.name+'.p <- '+ n.name+'.u')
                    ass.addConnection(n2, 'p', n, 'u')
        
        mad = Mad(ass)
        mad.run(True)

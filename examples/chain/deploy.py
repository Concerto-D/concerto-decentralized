import sys
from mad import *

from nodecomponent import Node

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("*** Error: missing parameters!\n")
        print("deploy.py <length of the chain>\n")
        sys.exit(-1)
    else:
        nbcomp = int(sys.argv[1])
        if nbcomp < 1:
            print("*** Warning: at least 1 user component is deployed by "
                  "this example. 1 component will be deployed.\n")
            nbcomp = 1

        # Composant Provider
        ass = Assembly()
        nodes = []

        for i in range(nbcomp):
            name = "n_" + str(i)
            nodes.append(Node(i==0, i==nbcomp-1))
            ass.addComponent(name, nodes[i])
            print("new component: "+name)
            if i>0:
                ass.addConnection(nodes[i-1], 'p', nodes[i], 'u')
                print("new connection: "+nodes[i-1].name+'.p -> '+ nodes[i].name+'.u')
        
        mad = Mad(ass)
        mad.run(True)

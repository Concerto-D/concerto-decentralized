import sys
from mad import *

from examples.scalability.provider import Provider
from examples.scalability.user_Ntrans import UserNTrans

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("*** Error: missing parameters!\n")
        print("deploy_par_up.py <number of user components> <number of "
              "transitions inside user components>\n")
        sys.exit(-1)
    else:
        nbcomp = int(sys.argv[1])
        nbtrans = int(sys.argv[2])
        if nbcomp < 1:
            print("*** Warning: at least 1 user component is deployed by "
                  "this example. 1 component will be deployed.\n")
            nbcomp = 1
        if nbtrans < 1:
            print("*** Warning: at least 1 transition is needed inside the "
                  "user components. 1 transition will be deployed.\n")
            nbtrans = 1

        # Composant Provider
        provider = Provider()
        ass = Assembly()
        ass.addComponent('provider', provider)

        users = []

        for i in range(0, nbcomp):
            users.append(UserNTrans())
            users[i].createTransitions(nbtrans)
            name = "u" + str(i)
            ass.addComponent(name, users[i])
            ass.addConnection(provider, 'service', users[i], 'service')

        mad = Mad(ass)
        mad.run()

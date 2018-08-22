import sys
from mad import *

from examples.scalability.provider import Provider
from examples.scalability.user_Ntrans import UserNTrans

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("*** Error: missing parameters!\n")
        print("deploy_par_up.py <number of components> <number of transitions>\n")
        sys.exit(-1)

    # Composant Provider
    provider = Provider()
    ass = Assembly()
    ass.addComponent('provider', provider)

    nbcomp = sys.argv[1]
    nbtrans = sys.argv[2]

    # first user
    u0 = UserNTrans()
    u0.createTransitions(nbtrans)
    ass.addComponent('u0', u0)

    ass.addConnection(provider, 'service', u0, 'service')

    for i in range(1, int(nbcomp)):
        exec("u" + str(i) + " = UserNTrans()")
        exec("u" + str(i) + ".createTransitions(" + nbtrans + ")")
        exec("ass.addComponent('u" + str(i) + "'," + "u" + str(i) + ")")
        exec("ass.addConnection(provider, 'service', u" + str(i)
             + ", 'service')")

    mad = Mad(ass)
    mad.run()

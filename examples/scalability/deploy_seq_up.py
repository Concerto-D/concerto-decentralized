import sys
from mad import *

from examples.scalability.provider import Provider
from examples.scalability.user import User
from examples.scalability.userprovider import UserProvider

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("*** Error: missing parameter!\n")
        print("deploy_seq_up.py <number of components to deploy "
              "sequentially>\n")
        sys.exit(-1)
    else:
        num = int(sys.argv[1])
        if num < 2:
            print("*** Warning: at least 2 components are deployed by this "
              "example. 2 components will be deployed.\n")
            num = 2


        # Composant Provider
        provider = Provider()
        ass = Assembly()
        ass.addComponent('provider', provider)

        # list of user-providers
        ups = []

        # user-providers created only if N > 2
        for i in range(0, num-2):
            ups.append(UserProvider())
            name = "up" + str(i)
            ass.addComponent(name, ups[i])
            if i > 0:
                ass.addConnection(ups[i-1], 'servicep', ups[i], 'serviceu')
            else:
                ass.addConnection(provider, 'service', ups[i], 'serviceu')

        # last user
        user = User()
        ass.addComponent('user', user)
        if num <= 2:
            ass.addConnection(provider, 'service', user, 'serviceu')
        else:
            ass.addConnection(ups[num-3], 'servicep', user, 'serviceu')

        mad = Mad(ass)
        mad.run()

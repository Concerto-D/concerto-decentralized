import sys
from mad import *

from examples.scalability.provider import Provider
from examples.scalability.user import User
from examples.scalability.userprovider import UserProvider

if __name__ == '__main__':

    # Composant Provider
    provider = Provider()
    ass = Assembly()
    ass.addComponent('provider', provider)

    # first user-provider
    up0 = UserProvider()
    ass.addComponent('up0', up0)

    ass.addConnection(provider, 'service', up0, 'serviceu')

    num = sys.argv[1]
    for i in range(1, int(num)-1):
        exec("up" + str(i) + " = UserProvider()")
        exec("ass.addComponent('up" + str(i) + "'," + "up" + str(i) + ")")
        exec("ass.addConnection(up" + str(i-1) + ", 'servicep', up"
             + str(i) + ", 'serviceu')")

    # last user
    user = User()
    ass.addComponent('user', user)
    exec("ass.addConnection(up" + str(int(num)-2)
         + ",'servicep', user, 'serviceu')")

    mad = Mad(ass)
    mad.run()
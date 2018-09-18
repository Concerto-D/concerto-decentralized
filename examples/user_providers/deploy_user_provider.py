from mad import *

from provider import Provider
from user import User

if __name__ == '__main__':

    # Composant User
    user = User()

    # Composant Provider
    provider = Provider()

    ass = Assembly()
    ass.addComponent('user', user)
    ass.addComponent('provider', provider)
    ass.addConnection(user, 'ipprov', provider, 'ip')
    ass.addConnection(user, 'service', provider, 'service')

    mad = Mad(ass)
    mad.run()
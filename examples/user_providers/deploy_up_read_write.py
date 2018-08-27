from mad import *

from provider_write import ProviderWrite
from user_read import UserRead

if __name__ == '__main__':

    # Composant User 1
    user1 = UserRead()
    user1.create()

    # Composant User 2
    user2 = UserRead()
    user2.create()

    # Composant Provider
    provider = ProviderWrite()
    provider.create()

    ass = Assembly()
    ass.addComponent('user1', user1)
    ass.addComponent('user2', user2)
    ass.addComponent('provider', provider)
    ass.addConnection(user1, 'ipprov', provider, 'ip')
    ass.addConnection(user1, 'service', provider, 'service')
    ass.addConnection(user2, 'ipprov', provider, 'ip')
    ass.addConnection(user2, 'service', provider, 'service')

    mad = Mad(ass)
    mad.run()
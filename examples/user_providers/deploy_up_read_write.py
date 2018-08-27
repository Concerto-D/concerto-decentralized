from mad import *

from provider_write import ProviderWrite
from user_read import UserRead

if __name__ == '__main__':

    # Composant User
    user = UserRead()
    user.create()

    # Composant Provider
    provider = ProviderWrite()
    provider.create()

    ass = Assembly()
    ass.addComponent('user', user)
    ass.addComponent('provider', provider)
    ass.addConnection(user, 'ipprov', provider, 'ip')
    ass.addConnection(user, 'service', provider, 'service')

    mad = Mad(ass)
    mad.run()
from mad import *

from provider_groups import ProviderGroups
from user import User

if __name__ == '__main__':

    # Composant User
    user = User()

    # Composant Provider
    provider = ProviderGroups()

    ass = Assembly()
    ass.addComponent('user_group', user)
    ass.addComponent('provider_group', provider)
    ass.addConnection(user, 'ipprov', provider, 'ip')
    ass.addConnection(user, 'service', provider, 'service')

    mad = Mad(ass)
    mad.run()
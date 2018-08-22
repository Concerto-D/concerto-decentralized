from mad import *

from provider_groups2 import ProviderGroups2
from user_groups import UserGroups

if __name__ == '__main__':

    # Composant User
    user = UserGroups()

    # Composant Provider
    provider = ProviderGroups2()

    ass = Assembly()
    ass.addComponent('user_group2', user)
    ass.addComponent('provider_group2', provider)
    ass.addConnection(user, 'service', provider, 'service')

    mad = Mad(ass)
    mad.run()
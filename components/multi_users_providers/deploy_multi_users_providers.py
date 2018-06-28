# -*- coding: utf-8 -*-

from assembly import Assembly
from components.multi_users_providers.provider import Provider
from components.multi_users_providers.user_provider import UserProvider

NB_USERPROVIDER = 5

# Instanciate the two components:
provider = Provider()

tab = []
tab.append([provider, 'provider'])
for i in range(NB_USERPROVIDER):
    exec("user_provider_" + str(i) + " = UserProvider()")
    exec("tab.append([user_provider_" + str(i) + ", "
            "'user_provider_' + str(i)])") 

# Instanciate the assembly:
assembly = Assembly(tab)

# Run the deployment while the two components are not connected:
assembly.auto_run()

# Check the current state:
assembly.check_dep()
provider.current_places
user_provider_0.current_places

# Connect Provider to the first UserProvide:
provider.net.ports['provide'].connect(user_provider_0.net.ports['use'])

assembly.check_dep()
user_provider_0.current_places

for i in range(NB_USERPROVIDER - 1):
    exec("user_provider_" + str(i) + ".net.ports['provide'].connect("
         "user_provider_" + str(i+1) + ".net.ports['use'])")

# Check the current state:
assembly.check_dep()


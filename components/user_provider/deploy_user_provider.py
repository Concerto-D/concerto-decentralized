# -*- coding: utf-8 -*-

from assembly import Assembly
from components.user_provider.user import User
from components.user_provider.provider import Provider


# Instanciate the two components:
user = User()
provider = Provider()

# Instanciate the assembly:
assembly = Assembly([
    [user, 'user'],
    [provider, 'provider']
])

# Run the deployment while the two components are not connected:
assembly.auto_run()

# Check the current state:
assembly.check_dep()
user.current_places
provider.current_places

# Connect the two components which leads to finish the deployment:
assembly.auto_connect('user', 'provider')

# Check the current state:
assembly.check_dep()
user.current_places
provider.current_places


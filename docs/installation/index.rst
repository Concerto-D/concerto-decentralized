.. _installation:

Installation
===============================

Code
-------

Madeus is available online on ``https://gitlab.inria.fr``. Anyone can create an account on this platform and download the source code for free. Please follow this `direct link <https://gitlab.inria.fr/Madeus/mad>`_ to the repository.


Installation
--------------

- MAD needs ``python3`` to run.

- It is more convenient to set the python environment variable ``export PYTHONPATH=/path/to/mad:$PYTHONPATH``. You can also put this command inside your ``.bashrc`` to get MAD permanently available.


Check installation
--------------------

- Go to your MAD directory

- Move to the examples directory ``cd examples/user_providers``

- run this command: ``python3 deploy_user_provider.py``

If everything went well, you should observe the following output:

.. code-block:: console

  [Mad] Assembly checked
  [Mad] Start assembly deployment
  [provider] Start transition 'init' ...
  [provider] End transition 'init'
  [provider] In place 'initiated'
  [provider] Start transition 'config' ...
  [provider] End transition 'config'
  [provider] In place 'configured'
  [Assembly] Enable connection (user, ipprov, provider, ip)
  [user] Start transition 'init' ...
  [provider] Start transition 'start' ...
  [provider] End transition 'start'
  [provider] In place 'started'
  [Assembly] Enable connection (user, service, provider, service)
  [user] End transition 'init'
  [user] In place 'initiated'
  [user] Start transition 'config' ...
  [user] End transition 'config'
  [user] In place 'configured'
  [user] Start transition 'start' ...
  [user] End transition 'start'
  [user] In place 'started'
  [Mad] Successful deployment

This example will be explained in detail in the Getting Started.

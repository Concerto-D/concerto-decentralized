Building a simple LAMP stack and deploying Application using MAD and Ansible Playbooks.
-------------------------------------------

The deployment is described by three MAD components with two places and a single transition.
Dependencies are built such that a sequential deployment is performed:
1. common
2. web
3. db

The initial Ansible playbook has been divided in three parts:
1. plb_common.yml
2. plb_web.yml
3. plb_db.yml

Each MAD component launch Ansible with the associated playbook inside its single transition.

The host file needs to be modified if you make a deployment on remote hosts.
Please also note that if you perform the deployment on remote hosts you need to configure ssh connections through ssh keys.
        [webservers]
        localhost

        [dbservers]
        localhost

The stack can be deployed using the following command:

        python deploy_lamp_seq.py

Python 3.6 is needed.

# Architecture
Concerto-D is composed of 3 repositories:
- **concerto-decentralized** which contains the code of Concerto for the asynchronous and synchronous version:
the reconfiguration language, the assemblies, the components, etc.
- **evaluation** which contains the code for doing experiments on Grid5000 and gather results 
and the code of the synthetic use case.
- **experiment_files** which contains the synthetic use case parameters used for the experiment 
(transitions times and nodes uptimes) and which also contains the results presented in the paper.

**Note:** the project has only be tested on **Linux** machines.

# Experiment
This is to reproduce the experiment to get the results from the paper. It can be run
locally on your computer or remotely on g5k. The setup is common for both cases except for few exceptions that
will be pointed out.

**Note:** To run the experiment locally or remotely you need a **g5k account**.

### Setup g5k credentials and access
*Set g5k credentials*
- If local: create the file ```~/.python-grid5000.yaml``` with the following content:
```
username: <g5k_username>
password: "<g5k_password>"
```
- If on g5k: the authentication should works out of the box, so the content should just be:
```
verify_ssl: /etc/ssl/certs/ca-certificates.crt
```
Cf https://msimonin.gitlabpages.inria.fr/python-grid5000/#installation-and-examples for more
informations

*Set g5k access*
- Make you have your **grid5000 ssh private key** put in .ssh folder
The evaluation code uses the ssh config file to configure its access to g5k:
- Create or modify the file ```~/.ssh/config``` and add the following rules:
```
Host g5k
  HostName access.grid5000.fr
  User <g5k_username>
  IdentityFile "<g5k_private_key>"
  ForwardAgent no
  
  # The following entries are added for local execution to use only one ssh connection to g5k. Enoslib by default
  # create as many ssh connection as the number of node it reserves
  ControlMaster auto
  ControlPath /dev/shm/ssh-g5k-master

 Host *.grid5000.fr
  User <g5k_username>
  ProxyCommand ssh g5k -W "$(basename %h .g5k):%p"
  IdentityFile "<g5k_private_key>"
  ForwardAgent no
```

### Setup experiment
*Create a empty dir and clone the repositories inside*
- ```mkdir concerto_d_evaluation```
- ```cd concerto_d_evaluation```
- - Clone the **experiment_files** repository:
  - ```git clone -b clean git@gitlab.inria.fr:aomond-imt/concerto-d/experiment_files.git```
  - or ````git clone -b clean https://gitlab.inria.fr/aomond-imt/concerto-d/experiment_files.git```` 
- Clone the **evaluation** repository: 
  - ```git clone -b clean git@gitlab.inria.fr:aomond-imt/concerto-d/evaluation.git```
  - or ````git clone -b clean https://gitlab.inria.fr/aomond-imt/concerto-d/evaluation.git````

*Configure the experiment parameters*
The file **evaluation/expe_template.yaml** contains the differents parameters of the experiments. It is an example
of a configuration but you are free to modify this file and to define the parameters that you want.
Each parameter is directly explained in the file.

*Install apt deps*
- ```sudo apt update```
- ```sudo apt install python3-pip virtualenv```

*Set up Python evaluation project:*
- ```cd evaluation``` go in the repository
- ```virtualenv venv``` create a Python virtual environment
- ```source venv/bin/activate``` activate the environment
- ```pip install -r requirements.txt``` install the dependencies of the project

### Execution
Assuming the previous step were executed.
- If local execution: ```ssh g5k``` create a dummy ssh connection to g5k. Every other connections to g5k will go through this one.
- ```source set_python_path.sh```
- ```python experiment/execution_experiment.py expe_template.yaml```

### Gather results
The logs files of the execution are located on g5k in **<remote_project_dir>/execution-<expe_name>-<datetime_expe_execution>**

The global experiments dir is located in **<local_project_dir>/global-<expe_name>-dir**
The result for each experiment is located in **<local_project_dir>/global-<expe_name>-dir/execution-<expe_name>-<datetime_expe_execution>**.
The files located in **<local_project_dir>/global-<expe_name>-dir/execution-<expe_name>-<datetime_expe_execution>/log_files_assemblies**
output the time for each part of the execution of the reconfiguration of each assembly, which serves to compute the global
result at the end.
The global result for an experiment is computed in this file: **<local_project_dir>/global-<expe_name>-dir/execution-<expe_name>-<datetime_expe_execution>/results_<concerto_d_version>_T<transition_time_id>_perc-<min_overlap>-<max_overlap>_expe_<waiting_rate>.json**   # TODO: à modifier le nom n'est plus d'actu

The log of the execution the controller of all the experiment is in **<local_project_dir>/global-<expe_name>-dir/experiment_logs/experiment_logs_<datetime_controller_execution>.txt**

In **<local_project_dir>/global-<expe_name>-dir/sweeps** the state of the sweeper is preserved. The sweeper is part of the
execo python library and keeps track of the current state of the execution of experiments. In our case, it marks experiments
as either *todo* if it has to be done *done* if finished correctly, *in_progress* if in progress(or if the whole process crash) and 
*skipped* if an exception occurs during the execution. More informations here: https://mimbert.gitlabpages.inria.fr/execo/execo_engine.html?highlight=paramsweeper#execo_engine.sweep.ParamSweeper

# TODO:
- Bien précisé ce que c'est qu'une experiment
- put projects in public and remove gitlab deploy keys etc
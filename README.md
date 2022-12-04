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
This part deals with the re-execution of the experiments done with the synthetic use case presented in the paper.\ 
The execution can be done either locally or remotely directly on g5k. The former is good for testing or debugging purposes,
the latter is better for long-term experiments.\
The setup is similar for both cases, with few differences. 

**Note:** To run the experiment locally or remotely you need a **g5k account**.

### Setup g5k credentials and access
*Set g5k credentials*
- If the execution is local: create the file ```~/.python-grid5000.yaml``` with the following content:
```
username: <g5k_username>
password: "<g5k_password>"
```
- If on g5k: the authentication should works out of the box, so the content should just be:
```
verify_ssl: /etc/ssl/certs/ca-certificates.crt
```
More informations on python-grid5000 here: https://msimonin.gitlabpages.inria.fr/python-grid5000/#installation-and-examples

**For local execution:** 
*Set g5k access*
- The **grid5000 ssh private key** is needed to access g5k. Then, it is required to add or modify some rules in the **ssh config 
file** as the evaluation code uses the ssh config file to configure its access to g5k:
- Create or modify the file ```~/.ssh/config``` and add the following rules:
```
Host g5k
  HostName access.grid5000.fr
  User <g5k_username>
  IdentityFile "<g5k_private_key>"
  ForwardAgent no
  
  # The following entries are added for local execution to use only one ssh connection to g5k. Enoslib by default
  # create as many ssh connection as the number of node it reserves which makes g5k to refuse some of the connections
  ControlMaster auto
  ControlPath /dev/shm/ssh-g5k-master

 Host *.grid5000.fr
  User <g5k_username>
  ProxyCommand ssh g5k -W "$(basename %h .g5k):%p"
  IdentityFile "<g5k_private_key>"
  ForwardAgent no
```

### Setup experiment
*Create a project dir and clone the repositories*
- ```mkdir <all_expes_dir>```
- ```cd <all_expes_dir>```
- - Clone the **experiment_files** repository:
  - ```git clone git@gitlab.inria.fr:aomond-imt/concerto-d/experiment_files.git```
  - or ````git clone https://gitlab.inria.fr/aomond-imt/concerto-d/experiment_files.git```` 
- Clone the **evaluation** repository: 
  - ```git clone git@gitlab.inria.fr:aomond-imt/concerto-d/evaluation.git```
  - or ````git clone https://gitlab.inria.fr/aomond-imt/concerto-d/evaluation.git````
  
*Configure the experiment parameters*

The file ```evaluation/expe_parameters.yaml``` contains the differents parameters of the experiments. This will be fed to the
python script that starts the experiment. This file contains an example of a configuration. **For each experiments** to run,
this has to be **adapted** before being passed as a parameter to the script.
Each parameter is directly explained in the file.

*Install apt deps*
- ```sudo apt update```
- ```sudo apt install python3-pip virtualenv```

*Set up Python evaluation project:*
- ```cd evaluation```
- ```virtualenv venv```
- ```source venv/bin/activate```
- ```pip install -r requirements.txt```

### Execution
Assuming the previous step were executed.
- If local execution: ```ssh g5k``` create a dummy ssh connection to g5k. Every other connections to g5k will go through this one.
- ```source set_python_path.sh```
- ```python experiment/execution_experiment.py expe_parameters.yaml```

### Gather results
There are two dirs created for the execution: **local dir** and **remote dir**.

The **remote dir** is ```<all_executions_dir>/execution-<expe_name>-<datetime_expe_execution>/``` and is always on g5k.
It contains mainly the log files of the assemblies for **debugging purposes**. 

The **local dir** is under the folder ```<all_expes_dir>/global-<expe_name>-dir/``` can be either on g5k or in your computer,
depending if you executed the script on g5k or locally. It contains:
- The execution dirs for each experiment: ```execution-<expe_name>-<datetime_expe_execution>``` which in turn contains:
  - The timestamp of each step of the reconfiguration in ```log_files_assemblies/```. These
  files serve to compute the global result at the end.
  - The global result of the experiment, computed in the file: ```results_<concerto_d_version>_T<transition_time_id>_perc-<min_overlap>-<max_overlap>_expe_<waiting_rate>.json```
- The log of the execution of the controller of all the experiment is in ```experiment_logs/experiment_logs_<datetime_controller_execution>.txt```
- The state of the ParamSweeper in ````sweeps/````. The sweeper is part of the
```execo``` python library and keeps track of the current state of the execution of experiments. In our case, it marks experiments
as either *todo* if it has to be done *done* if finished correctly, *in_progress* if in progress (or if the whole process crash) and 
*skipped* if an exception occurs during the execution.\ 
More informations here: https://mimbert.gitlabpages.inria.fr/execo/execo_engine.html?highlight=paramsweeper#execo_engine.sweep.ParamSweeper

### After the execution
If some experiments has been skipped or if not all experiments were run, it is possible to **launch again** the script
with **the same parameter file** (expe_parameters.yaml). Thanks to the param sweeper, it will automatically run the missing
experiments. However, it will **not** relaunch the experiments that are already done. To do that, you will need to change the
value of **<expe_name>**, because the sweeper base itself on it.

# Local execution
This part explains what to do if the goal is only to **start a reconfiguration manually** for **development or debugging purposes**.

### Setup local environment
*Create a project dir and clone the repositories*
- ```mkdir <all_projects_dir>```
- ```cd <all_projects_dir>```
- Clone the **concerto-decentralized** repository: 
  - ```git clone git@gitlab.inria.fr:aomond-imt/concerto-d/concerto-decentralized.git```
  - or ````git clone https://gitlab.inria.fr/aomond-imt/concerto-d/concerto-decentralized.git````
- - Clone the **experiment_files** repository:
  - ```git clone git@gitlab.inria.fr:aomond-imt/concerto-d/experiment_files.git```
  - or ````git clone https://gitlab.inria.fr/aomond-imt/concerto-d/experiment_files.git```` 
- Clone the **evaluation** repository: 
  - ```git clone git@gitlab.inria.fr:aomond-imt/concerto-d/evaluation.git```
  - or ````git clone https://gitlab.inria.fr/aomond-imt/concerto-d/evaluation.git````

*Install apt deps*
- ```sudo apt update```
- ```sudo apt install python3-pip virtualenv```

*Set up Python evaluation project:*
- ```cd concerto-decentralized```
- ```virtualenv venv```
- ```source venv/bin/activate```
- ```pip install -r requirements.txt```

### Start execution of a script
Position in concerto-decentralized dir and activate environment **if not already done**:
```
cd concerto-decentralized
source venv/bin/activate
source source_dir.sh
```
There is no orchestrator in local, scripts has to be started manually. The call of a script is like this:
```
# Start the server
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_server.py <config_file_path> <uptime_duration> <waiting_rate> <timestamp_log_dir> <execution_expe_dir> <version_concerto_d> &

# Start a dependency (need an additionnal <dep_num> arg)
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_dep.py <config_file_path> <uptime_duration> <waiting_rate> <timestamp_log_dir> <execution_expe_dir> <version_concerto_d> <dep_num> &
```
Example of calls 1 serv and 3 deps
```
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_server.py ../experiment_files/parameters/transitions_times/transitions_times-1-30-deps12-0.json 30 1 . . synchronous &    # Server
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_dep.py ../experiment_files/parameters/transitions_times/transitions_times-1-30-deps12-0.json 30 1 . . synchronous 0 &    # Dep 0
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_dep.py ../experiment_files/parameters/transitions_times/transitions_times-1-30-deps12-0.json 30 1 . . synchronous 1 &    # Dep 1
python3 ../evaluation/synthetic_use_case/reconf_programs/reconf_dep.py ../experiment_files/parameters/transitions_times/transitions_times-1-30-deps12-0.json 30 1 . . synchronous 2 &    # Dep 2
```
**Notes:** 
- The **number of deps launched** has to match **all the <nb_deps_tot> variables** present in <config_file_path>. Here
in the example with 3 deps it has to be <nb_deps_tot> equal to 3 in the config file. It cannot go beyond 12 deps.
- Launching scripts like this is the equivalent of having **100% overlap** between units.
- The results are not computed here (total reconf time, etc).

# TODO:
- put projects in public and remove gitlab deploy keys etc
- Mettre concerto-d-synchrone dans la liste au début + faire un test avec le tag ICSOC

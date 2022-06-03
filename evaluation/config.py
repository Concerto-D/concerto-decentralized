NB_DEPS_TOT = 2

# Dummy values for server
t_sc, t_ss, t_sp = [], [], []
for i in range(NB_DEPS_TOT):
    t_sc.append(i + 1)
    t_ss.append(i + 2)
    t_sp.append(i + 3)

COMPONENTS_PARAMETERS = {
    "server": [1, t_sc, 4, t_ss, t_sp],
}

# Ids values for deps
for i in range(NB_DEPS_TOT):
    COMPONENTS_PARAMETERS[f"dep{i}"] = [i]


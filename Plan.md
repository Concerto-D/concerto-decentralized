- I - fin implémentation - 1 semaine
  - Concerto asynchrone = Concerto qui se rendort
  - Mettre en place de la persistence
    - Identifier les choses à persister
    - Tester le dump JSON et voir si on enlève des choses (déduit)
    - Voir pour le pb des références
  - Voir pour la notion d'actif, voir s'il faut rajouter un autre actif que celui utilisé dans le code
  - Voir si le nb_users des dépendances est lié au fait qu'un groupe contient autant de port que de places dans le groupe
  - Rajouter l'id_sync en paramètre optionnel du wait_all
    - Valeur par défaut modifiable

- II - design des cas d'étude - 0.5 semaine
- III - coder les cas d'étude en Concerto et Muse - 1.5 semaines
- IV - expérimentations sur Grid'5000 - 0.5 semaine
- V - écriture du papier - 2.5 semaines

- Questions
  - Zenoh est thread-safe ?
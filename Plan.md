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

- II - design des cas d'étude - 1.5 semaine
  - Cas synthétique qui représentent tout ce qu'on veut montrer et qui traite tous les cas
  - Cas réel (déploiement du CNN, scaling genre ajouter plusieurs CNN, plusieurs OU qui prennent des photos, etc)
  - Comment simuler des machines proches des OUs (setup expérimental)
  - Scénarios d'expérimentation (simulation d'une durée de 10h)
  - Comment déployer tout ça, dire que les nodes dorment etc
- III - coder les cas d'étude en Concerto et Muse - 1.5 semaines
- IV - expérimentations sur Grid'5000 - 1.5 semaine
- V - écriture du papier - tout le long
  - Focus sur la partie Expérimentation et Solution

- Questions
  - Zenoh est thread-safe ?
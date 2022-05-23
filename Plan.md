- I - fin implémentation - 1 semaine
  - Revoir le connect et le disconnect + remote_connection
  - Avoir un workflow unique pour tout le monde:
    - Si la commande n'est pas terminée, elle return false
    - Un tour de sémantique est joué
    - S'il n'y a aucun token qui a bougé et qu'il n'y a aucune transition active,
    on fait la commande asynchrone
    - La commande mise en attente du début est reprise là où elle n'avait pas terminée
  - Virer les data_provides et data_use

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
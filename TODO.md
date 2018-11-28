* TODOs

** Urgent

- Corriger suppression de DataProvider

** Vérifications

- Vérifier que le groupes se comportent comme prévu

** Fonctionalités

- Ne pas bloquer lors de deux change_behavior consécutifs
- Gantt chart : exporter dans un format automatiquement dessinable
- Vérifier que les noms de composants / transitions / groupes / places / comportements ne contiennent pas ',' et ne commencent pas par '_' (pour évolutions futures)
- Clarifier le cas où la place initiale est dans un groupe (pour l'instant : interdit)
- Gérer les ports de la place initiale (suggestion : mettre un token dans un dock input au lieu de la place directement)
- Puis créer un meilleure composant DataProvider
- Gérer dépendance sur tout le composant
- Gérer les ports optionnels
- Plusieurs comportements pour les transitions

** Corrections par rapport à la sémantique formelle

- Groupes : gérer le cas où plusieurs groupes sont connectés à un port : ET au lieu de OU
- Vrai "switch"

** Code

- Documentation

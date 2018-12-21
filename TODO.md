* TODOs

** Urgent

- Corriger suppression de DataProvider

** Vérifications

- Vérifier que le groupes se comportent comme prévu
- Vérifier que la transition _init a résolu les problèmes de ports sur l'état initial et de groupes contenant l'état initial

** Fonctionalités

- Discuter de la sémantique du composant : faire les quatre étapes d'un coup ou une seule ? Modifié actuallement aux quatre étapes d'un coup en commençant par idocks to place pour ne pas fournir un provide si l'état n'est pas stable
- S'assurer que la sémantique "on ne peut pas quitter une place deux fois dans le même comportement" correspond à ce qui est attendu (objectif : éviter les boucles)
- Vérifier que les noms de composants / transitions / groupes / places / comportements ne contiennent pas ',' et ne commencent pas par '_' (pour évolutions futures)
- Gérer dépendance sur tout le composant
- Gérer les ports optionnels
- Plusieurs comportements pour les transitions

** Corrections par rapport à la sémantique formelle

- Groupes : gérer le cas où plusieurs groupes sont connectés à un port : ET au lieu de OU
- Vrai "switch"

** Code

- Documentation

** Modèle

- Conflits

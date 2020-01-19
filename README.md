# rpg_helper

L’idée ce serait de faire un programme en python qui génère un petit serveur web (avec la library dash). 

Le MJ à accès au pc qui fait tourner le programme et les joueur se connectent avec leur navigateur internet sur leur téléphone portable.  

Les joueur voient une page avec leur différentes stats (force/agilité/présence etc).

à côté de chacune des stats il y a un bouton pour lancer un test :
le MJ reçoit la requête de test, le joueur explique pourquoi il fait un test
le MJ décide de la difficulté du test en tapant un nombre sur son ordi, le résultat est calculé en fonction des stats du joueur et de la difficulté et est affiché sur la page du joueur et du MJ.
Le mj peut lancer un test, une bar de temps apparaît sur la page des joueur qui peuvent réagir en cliquant. En fonction de leur temps de réaction leur test seront affectés. 

Ce qu’il faut:
Mettre en forme les pages des joueurs
Designer les différentes classes/stats
Ecrire le mécanisme de calcul des tests
Ecrire le mécanisme de stats des joueur ( script de création: choix de classe, choix d’affinité ⇒ génère un fichier avec des stats / script de lecture des fichier de stats pour les prendre en compte lors du lancement du programme)
Mécanisme de lancement de test des joueur et du MJ

Theme: mediévale fantastique (D&D)
Ethnies: orcs elfes humains
Classe: Mage, guerrier, archer, voleur
Stats:Force / agilité / charisme / intelligence / constitution

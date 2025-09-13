## TODO:
 - backup file finder
 - USER_AGENT  + proxy rotation random pour dirfinder pour eviterde se faire err 429
  - rajouter un truc pour directement lancer une commande genre python3 main.py --tools=dirfinder localhost:8000....
  - remove pycache from github repo



  
DIRFINDER
Ajouter une option pour sauvegarder les résultats dans un fichier (scan_results.txt ou json).

Config réutilisable :

Lire une config depuis un fichier .toml ou .yaml (target, wordlist, threads, proxy) → ça évite de tout retaper.

User-Agent rotation :
Charger une liste d’USER_AGENT randomisés depuis un fichier, ça aide à éviter certains filtres.

Headers personnalisés :
Ajouter une option pour passer des headers custom (Authorization, Cookie, etc.).
relancer X fois si une requête échoue.

Filtrage par taille :
	Beaucoup d’outils filtrent les réponses par taille (ex: ignorer toutes les 404 qui font 1234 bytes).
	Tu pourrais afficher la taille de la réponse, et laisser l’utilisateur définir un filtre (--exclude-size 1234).

Auto-wordlist expansion :
	Quand tu trouves un répertoire (/admin/), relancer un scan à l’intérieur avec la même wordlist → exploration récursive.

Detection WAF / rate-limit :
	Si tu reçois trop de 429 Too Many Requests → ralentir la vitesse.
	Si tu détectes un WAF (Cloudflare, etc.), afficher un warning.

🔒 Sécurité & Robustesse

SSL strict / souple :

Actuellement tu ignores la vérification SSL → tu pourrais donner le choix (--insecure comme curl).

Gestion des erreurs enrichie :

Loguer les erreurs (timeout, refused, etc.) séparément pour debug.

proxy qui tourne
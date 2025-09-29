## TODO:
 - backup file finder: list generator puis scan
 - USER_AGENT  + proxy rotation random pour dirfinder pour eviterde se faire err 429
  - rajouter un truc pour directement lancer une commande genre python3 main.py --tools=dirfinder localhost:8000....



  
DIRFINDER
Ajouter une option pour sauvegarder les résultats dans un fichier (scan_results.txt ou json).

Config réutilisable :

Lire une config depuis un fichier .toml ou .yaml (target, wordlist, threads, proxy) → ça évite de tout retaper.

Headers personnalisés :
Ajouter une option pour passer des headers custom (Authorization, Cookie, etc.).



-> yea this is amazing!!!!!!! Auto-wordlist expansion :
	Quand tu trouves un répertoire (/admin/), relancer un scan à l’intérieur avec la même wordlist → exploration récursive.

Detection WAF / rate-limit :
	Si tu reçois trop de 429 Too Many Requests → ralentir la vitesse.
	Si tu détectes un WAF (Cloudflare, etc.), afficher un warning.

🔒 Sécurité & Robustesse

SSL strict / souple :

Actuellement tu ignores la vérification SSL → tu pourrais donner le choix (--insecure comme curl).

proxy qui tourne
file for urls

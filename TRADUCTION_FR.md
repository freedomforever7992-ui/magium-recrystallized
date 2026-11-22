# Version française de Magium Recrystallized (APK non officiel)

## Fonctionnement
- L'archive d'origine `static/magium.story` ne change pas.
- Le script `scripts/generate_french_story.py` extrait ses passages CYOA (12 noeuds narratifs dans la version actuelle) et les libellés des choix.
- Il utilise Argos Translate pour traduire en français pendant la compilation GitHub Actions.
- Il génère `static/magium-fr.json`, intégré dans l'APK. Le téléchargement du modèle n'est nécessaire que sur GitHub Actions, jamais sur le téléphone.
- Au lancement, `src/lib/wasm.ts` charge la traduction selon la langue choisie, sans changer les index et destinations des choix.
- La première scène et les principaux boutons de choix sont également traduits manuellement via `src/lib/story-fr-fallback.ts`.

## Utilisation
Aller dans l'onglet Actions, lancer `Magium Recrystallized - APK Android ARM64`, puis récupérer l'artefact APK après une compilation réussie.
Dans le jeu : **Menu > Paramètres > Langue** pour passer de français à anglais et inversement.

## Vérification et limites
- Les identifiants du jeu sont conservés. Les lignes de contrôle `#if`, `#else` et les accolades isolées ne sont jamais envoyées au traducteur.
- Les 12 scènes sont contrôlées à la fin de l'étape de traduction. Un échec de traduction arrête la compilation au lieu de fournir silencieusement un APK présenté comme entièrement traduit.
- La traduction de la narration est automatique : les dialogues peuvent demander une relecture stylistique et des corrections de vocabulaire.
- Les embranchements existants sont préservés mais aucun chapitre absent du projet amont n'est créé.
- Le site web sans `magium-fr.json` n'affiche qu'une traduction partielle (introduction et choix). L'APK généré par ce workflow inclut la narration traduite complète.
- Les statistiques illimitées modifient l'interface et sa sauvegarde locale. La logique des conséquences et des gardes narratifs du projet amont reste incomplète.

## Crédits
Le projet Magium Recrystallized est distribué sous AGPL-3.0 et attribue le jeu d'origine à Cristian Mihailescu. Cette traduction et ce portage sont non officiels et doivent conserver les avis de licence et les crédits du projet.

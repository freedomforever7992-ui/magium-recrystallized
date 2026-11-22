/** Hand-reviewed opening and every current choice; used if the build-time
 * translation bundle is absent (for example on the original web site).
 * The binary CYOA game is never modified. */
export const frenchOpening = `
On dit que la frontière entre le courage et la stupidité est extrêmement mince. Alors que je me tiens au milieu de cette forêt, les yeux rivés sur les explosions qui éclatent au loin, je prends conscience que j'ai sans doute franchi cette frontière... et qu'il est désormais trop tard pour faire demi-tour.

Je m'appelle Barry. J'ai vingt-huit ans et on pourrait me décrire, à juste titre, comme un homme tout à fait ordinaire. Je n'ai aucun talent, aucune compétence particulière, ni même de formation universitaire. La seule chose qui me distingue, c'est l'obsession qui m'habite depuis toujours : devenir un mage. C'est mon rêve depuis l'âge de cinq ans. Toute ma vie, cette passion m'a poussé à accumuler des connaissances sur les mages et à parcourir le monde à la recherche d'un moyen de réaliser mon souhait.

Après d'innombrables années passées à fouiller de vieux grimoires poussiéreux et des parchemins usés par le temps, j'ai enfin trouvé un moyen d'y parvenir.

Le problème ? Je dois d'abord remporter un tournoi contre les mages les plus puissants du monde. Cela paraît insensé ? C'est probablement parce que ça l'est. Mais il est beaucoup trop tard pour reculer. Il ne me reste qu'une direction : aller de l'avant.

Alors que je me tiens ici, conscient qu'il m'est désormais impossible de retrouver ma vie ordinaire, je ne peux m'empêcher de me sentir...
`;

export const frenchChoices: Record<string, string> = {
  'Excited': 'Enthousiaste',
  'Calm': 'Calme',
  'Afraid': 'Effrayé',
  'Stay silent': 'Garder le silence',
  'Show myself': 'Me montrer',
  'I see no reason to show myself to you.': 'Je ne vois aucune raison de me montrer.',
  'Give him until the count of ten to retreat': 'Lui laisser jusqu’à dix pour battre en retraite',
  "Imply that I'm the one who destroyed the city of Olmnar": 'Laisser entendre que j’ai détruit la ville d’Olmnar',
  'Restart game': 'Recommencer la partie',
  'Load game': 'Charger une partie',
  'Continue': 'Continuer',
  "Tell him I'm actually an ordinary human": 'Lui dire que je suis simplement un humain ordinaire',
  'Tell him my parents had a weird sense of humor': 'Lui dire que mes parents avaient un drôle de sens de l’humour',
  'Next chapter': 'Chapitre suivant',
  'Tell him the truth': 'Lui dire la vérité',
  'Tell him I was forced into it': 'Lui dire que j’y ai été contraint',
  "Tell him I'm looking for a cure for my sick sister": 'Lui dire que je cherche un remède pour ma sœur malade'
};

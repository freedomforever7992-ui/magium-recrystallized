import { writable } from 'svelte/store';

export type Language = 'fr' | 'en';
const dictionary = {
  fr: {
    menu: 'MENU', stats: 'STATS', book: 'LIVRE', chapter: 'CHAPITRE',
    headingStats: 'Statistiques', magicalPower: 'Puissance magique',
    magicalKnowledge: 'Connaissances magiques', availablePoints: 'Points disponibles',
    unlimited: 'Illimités', unlimitedMode: 'Mode statistiques illimitées',
    unlimitedHelp: 'Augmente chaque statistique librement et sans dépenser de points. Les valeurs sont conservées sur cet appareil.',
    engineWarning: 'Remarque : le moteur narratif de cette version ne relie pas encore toutes les conditions aux statistiques.',
    increase: 'Augmenter de', reduce: 'Diminuer de 1',
    resetStats: 'Remettre les statistiques à zéro',
    resetConfirm: 'Réinitialiser toutes les statistiques ?',
    strength:'Force', speed:'Vitesse', toughness:'Résistance', reflexes:'Réflexes',
    hearing:'Ouïe', observation:'Observation', languages:'Langues anciennes',
    combat:'Technique de combat', premonition:'Prémonition', bluff:'Bluff',
    magicalSense:'Sens magique', aura:'Renforcement de l’aura',
    quicksave:'Sauvegarde rapide', checkpoint:'Charger le dernier point',
    achievements:'Succès', saves:'Sauvegardes', settings:'Paramètres', about:'À propos',
    settingsTitle:'Paramètres', darkEnable:'Activer le mode sombre',
    darkDisable:'Désactiver le mode sombre', theme:'Thème', width:'Largeur du texte',
    fullWidth:'Pleine largeur', mediumWidth:'Trois quarts', halfWidth:'Moitié',
    language:'Langue', english:'Anglais', french:'Français',
    narrativeLanguage:'Les menus sont traduits. Le texte de l’histoire reste en anglais dans les données actuelles.',
    passage:'Passage actuel', saveAuto:'La progression est automatiquement enregistrée sur cet appareil.',
    saveNow:'Créer un point de sauvegarde', loadNow:'Charger le point de sauvegarde',
    restart:'Recommencer l’histoire', saved:'Sauvegarde enregistrée.',
    loaded:'Sauvegarde chargée.', noSave:'Aucune sauvegarde manuelle disponible.',
    restartConfirm:'Recommencer depuis le début ?'
  },
  en: {
    menu: 'MENU', stats: 'STATS', book: 'BOOK', chapter: 'CHAPTER',
    headingStats: 'Statistics', magicalPower: 'Magical power',
    magicalKnowledge: 'Magical knowledge', availablePoints:'Available points',
    unlimited:'Unlimited', unlimitedMode:'Unlimited statistics mode',
    unlimitedHelp:'Increase any statistic without spending points. Values are saved on this device.',
    engineWarning:'Note: the current story engine does not yet connect every narrative condition to statistics.',
    increase:'Increase by', reduce:'Decrease by 1',
    resetStats:'Reset statistics', resetConfirm:'Reset all statistics?',
    strength:'Strength', speed:'Speed', toughness:'Toughness', reflexes:'Reflexes',
    hearing:'Hearing', observation:'Observation', languages:'Ancient Languages',
    combat:'Combat Technique', premonition:'Premonition', bluff:'Bluff',
    magicalSense:'Magical sense', aura:'Aura hardening',
    quicksave:'Quicksave', checkpoint:'Last checkpoint',
    achievements:'Achievements', saves:'Saves', settings:'Settings', about:'About',
    settingsTitle:'Settings', darkEnable:'Enable dark mode',
    darkDisable:'Disable dark mode', theme:'Theme', width:'Text width',
    fullWidth:'Full width', mediumWidth:'Three quarters', halfWidth:'Half',
    language:'Language', english:'English', french:'French',
    narrativeLanguage:'Menus are translated. The story text is still English in the current story data.',
    passage:'Current passage', saveAuto:'Progress is automatically saved on this device.',
    saveNow:'Create checkpoint', loadNow:'Load checkpoint',
    restart:'Restart story', saved:'Checkpoint saved.',
    loaded:'Checkpoint loaded.', noSave:'No manual checkpoint available.',
    restartConfirm:'Restart from the beginning?'
  }
} as const;

export type TranslationKey = keyof typeof dictionary.fr;
function initialLanguage(): Language {
  if (typeof window === 'undefined') return 'fr';
  try {
    return window.localStorage.getItem('magium-language') === 'en' ? 'en' : 'fr';
  } catch { return 'fr'; }
}
export const language = writable<Language>(initialLanguage());
language.subscribe(lang => {
  if (typeof document === 'undefined') return;
  document.documentElement.lang = lang;
  try { localStorage.setItem('magium-language', lang); } catch {}
});
export function t(key: TranslationKey, lang: Language): string {
  return dictionary[lang][key];
}

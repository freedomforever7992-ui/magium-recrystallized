import { writable, type Writable } from 'svelte/store';

/** Stat names are kept in English internally for compatibility with the original code. */
export const baseKeys = [
  'Strength', 'Speed', 'Toughness', 'Reflexes', 'Hearing', 'Observation',
  'Ancient Languages', 'Combat Technique', 'Premonition', 'Bluff',
  'Magical sense', 'Aura hardening'
] as const;
export type StatKey = typeof baseKeys[number];
export type ExtraKey = 'magicalPower' | 'magicalKnowledge' | 'availablePoints';
export type AllKeys = StatKey | ExtraKey;
export type Stats = Record<AllKeys, number>;

export interface StatDelta {
  key: AllKeys;
  oldValue: number;
  newValue: number;
  timestamp: Date;
}
export interface DeltasStore {
  subscribe: Writable<StatDelta[]>['subscribe'];
  clear: () => void;
}
export interface StatsStore extends Writable<Stats> {
  deltas: DeltasStore;
  addStat: (key: AllKeys, amount: number) => void;
  resetDeltas: () => void;
  resetStats: () => void;
}

const STORAGE_KEY = 'magium-unlimited-stats-v1';
const initial: Stats = {
  Strength: 0, Speed: 0, Toughness: 0, Reflexes: 0, Hearing: 0,
  Observation: 0, 'Ancient Languages': 0, 'Combat Technique': 0,
  Premonition: 0, Bluff: 0, 'Magical sense': 0, 'Aura hardening': 0,
  magicalPower: 1, magicalKnowledge: 1, availablePoints: 4
};

function restore(): Stats {
  if (typeof localStorage === 'undefined') return {...initial};
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (!saved || typeof saved !== 'object') return {...initial};
    const next = {...initial};
    for (const key of Object.keys(initial) as AllKeys[]) {
      const value = saved[key];
      if (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0) next[key] = value;
    }
    return next;
  } catch { return {...initial}; }
}
function persist(value: Stats) {
  if (typeof localStorage === 'undefined') return;
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(value)); } catch {}
}

function createStatsStore(): StatsStore {
  const store = writable<Stats>(restore());
  store.subscribe(persist);
  const deltaStore = writable<StatDelta[]>([]);
  const deltas: DeltasStore = {
    subscribe: deltaStore.subscribe,
    clear: () => deltaStore.set([])
  };
  function addStat(key: AllKeys, amount: number) {
    if (key === 'availablePoints' || !Number.isSafeInteger(amount)) return;
    store.update(current => {
      const oldValue = current[key];
      // Unlimited allocation: no 4-point cap and no deduction from the points pool.
      const newValue = Math.max(0, Math.min(Number.MAX_SAFE_INTEGER, oldValue + amount));
      if (oldValue === newValue) return current;
      deltaStore.update(log => [...log.slice(-99), {
        key, oldValue, newValue, timestamp: new Date()
      }]);
      return {...current, [key]: newValue};
    });
  }
  function resetStats() {
    store.set({...initial});
    deltas.clear();
  }
  return {
    subscribe: store.subscribe, set: store.set, update: store.update,
    deltas, addStat, resetDeltas: deltas.clear, resetStats
  };
}
export const statsStore = createStatsStore();

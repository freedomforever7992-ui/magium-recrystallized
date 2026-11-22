<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { baseKeys, statsStore, type StatKey } from '$lib/stores/stats';
  import { uiState, PrimaryState, openGame } from '$lib/stores/state';
  import { language, t, type TranslationKey } from '$lib/i18n';

  const names: Record<StatKey, TranslationKey> = {
    'Strength': 'strength', 'Speed': 'speed', 'Toughness': 'toughness',
    'Reflexes': 'reflexes', 'Hearing': 'hearing',
    'Observation': 'observation', 'Ancient Languages': 'languages',
    'Combat Technique': 'combat', 'Premonition': 'premonition',
    'Bluff': 'bluff', 'Magical sense': 'magicalSense',
    'Aura hardening': 'aura'
  };
  function number(value: number): string {
    return value.toLocaleString($language === 'fr' ? 'fr-FR' : 'en-US');
  }
  function reset() {
    if (confirm(t('resetConfirm', $language))) statsStore.resetStats();
  }
  function keydown(e: KeyboardEvent) {
    if (e.key === 'Escape') openGame();
  }
</script>

<svelte:window on:keydown={keydown} />

{#if $uiState.primary === PrimaryState.Stats}
  <div class="fixed inset-0 bg-black/70 z-40" on:click={openGame}
       aria-hidden="true" transition:fade />

  <section role="dialog" aria-modal="true" aria-label={t('headingStats', $language)}
           class="fixed inset-0 z-50 overflow-y-auto bg-gray-50 dark:bg-gray-900 text-neutral-900 dark:text-neutral-100"
           in:fly={{ x: innerWidth, duration: 230 }}
           out:fly={{ x: innerWidth, duration: 230 }}>
    <div class="max-w-3xl mx-auto px-4 sm:px-8 pb-12 pt-6">
      <header class="flex items-center justify-between mb-5">
        <h2 class="text-2xl sm:text-3xl font-bold">{t('headingStats', $language)}</h2>
        <button on:click={openGame} aria-label="Fermer / Close"
                class="rounded-lg bg-gray-800 dark:bg-gray-100 text-white dark:text-gray-900 px-4 py-2 text-lg">✕</button>
      </header>

      <div class="rounded-xl border border-amber-600/40 p-4 mb-6 bg-amber-700/10">
        <p class="text-lg font-semibold">{t('unlimitedMode', $language)} · ∞</p>
        <p class="mt-1 text-sm">{t('unlimitedHelp', $language)}</p>
        <p class="mt-2 text-xs opacity-80">{t('engineWarning', $language)}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        {#each [
          {key: 'magicalPower' as const, label: 'magicalPower' as const},
          {key: 'magicalKnowledge' as const, label: 'magicalKnowledge' as const}
        ] as extra}
          <div class="rounded-xl bg-gray-200 dark:bg-gray-800 p-3">
            <div class="flex items-center justify-between mb-3">
              <span class="font-semibold">{t(extra.label, $language)}</span>
              <strong>{number($statsStore[extra.key])}</strong>
            </div>
            <div class="flex justify-end gap-2">
              <button on:click={() => statsStore.addStat(extra.key, 1)}
                      class="rounded bg-gray-700 text-white px-3 py-2">+1</button>
              <button on:click={() => statsStore.addStat(extra.key, 10)}
                      class="rounded bg-gray-700 text-white px-3 py-2">+10</button>
              <button on:click={() => statsStore.addStat(extra.key, 100)}
                      class="rounded bg-gray-700 text-white px-3 py-2">+100</button>
            </div>
          </div>
        {/each}
      </div>

      <p class="mb-4 font-semibold">{t('availablePoints', $language)} : ∞</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {#each baseKeys as key}
          <div class="rounded-xl border border-gray-300 dark:border-gray-700 px-3 py-3">
            <div class="flex justify-between items-center gap-3 mb-3">
              <span class="font-semibold">{t(names[key], $language)}</span>
              <span class="font-bold tabular-nums">{number($statsStore[key])}</span>
            </div>
            <div class="flex gap-2 justify-end">
              <button on:click={() => statsStore.addStat(key, -1)}
                      title={t('reduce', $language)}
                      class="rounded bg-gray-300 dark:bg-gray-700 px-3 py-2">−1</button>
              {#each [1, 10, 100] as amount}
                <button on:click={() => statsStore.addStat(key, amount)}
                        title={t('increase', $language) + ' ' + amount}
                        class="rounded bg-gray-800 text-white dark:bg-gray-100 dark:text-gray-900 px-3 py-2">+{amount}</button>
              {/each}
            </div>
          </div>
        {/each}
      </div>
      <button on:click={reset}
              class="mt-7 w-full border border-red-500 rounded-lg p-3 text-red-600 dark:text-red-400">
        {t('resetStats', $language)}
      </button>
    </div>
  </section>
{/if}

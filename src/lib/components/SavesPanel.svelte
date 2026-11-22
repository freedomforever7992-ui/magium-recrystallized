<script lang="ts">
  import { currentIndex, saveCheckpoint, loadCheckpoint, restartStory } from '$lib/stores/passagestore';
  import { closeMenu } from '$lib/stores/state';
  import { language, t } from '$lib/i18n';

  let feedback = '';
  function save() { saveCheckpoint(); feedback = t('saved', $language); }
  function load() {
    if (loadCheckpoint()) { feedback = t('loaded', $language); closeMenu(); }
    else feedback = t('noSave', $language);
  }
  function restart() {
    if (confirm(t('restartConfirm', $language))) {
      restartStory();
      closeMenu();
    }
  }
</script>
<section class="p-6 pt-20 space-y-5 text-neutral-900 dark:text-neutral-100">
  <h2 class="text-3xl font-bold">{t('saves', $language)}</h2>
  <p>{t('saveAuto', $language)}</p>
  <p>{t('passage', $language)} : {$currentIndex}</p>
  <button class="block w-full rounded bg-gray-700 text-white p-4" on:click={save}>{t('saveNow', $language)}</button>
  <button class="block w-full rounded bg-gray-700 text-white p-4" on:click={load}>{t('loadNow', $language)}</button>
  <button class="block w-full rounded bg-red-900 text-white p-4" on:click={restart}>{t('restart', $language)}</button>
  <p aria-live="polite">{feedback}</p>
</section>

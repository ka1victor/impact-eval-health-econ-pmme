<template>
  <div class="fonte-band">
    <span class="fonte-lbl">{{ rotulo }}</span>
    <span class="fonte-txt"><slot /></span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ rotulo?: string }>(), { rotulo: 'Fontes' });
</script>

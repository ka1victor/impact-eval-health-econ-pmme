<template>
  <figure class="fig-box" :class="{ 'fig-fill': preenche }">
    <img :src="src" :alt="alt" :style="preenche ? undefined : { maxHeight: h }" />
  </figure>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{ src: string; alt?: string; h?: string }>(), {
  h: '18rem',
  alt: '',
});

// h="fill": a figura consome a altura livre da página, sem distorcer.
const preenche = computed(() => props.h === 'fill');
</script>

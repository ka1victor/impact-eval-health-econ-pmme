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
// ATENÇÃO: só funciona DENTRO de uma linha `.cols.fill`, que estica o pai.
// Solta num slide, o pai fica com altura zero e a imagem, posicionada em
// `inset: 0`, desaparece sem erro. Fora de `.cols.fill`, passe uma altura
// explícita, como h="16rem".
const preenche = computed(() => props.h === 'fill');
</script>

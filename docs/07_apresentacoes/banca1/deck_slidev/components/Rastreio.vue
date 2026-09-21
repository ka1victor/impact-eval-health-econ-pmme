<template>
  <div class="rastreio-band">
    <span class="rastreio-txt"><slot /></span>
    <span class="rastreio-right">
      <span v-if="cont" class="rastreio-cont">{{ cont }}</span>
      <span v-if="!semnum" class="rastreio-num"><SlideCurrentNo /> / <SlidesTotal /></span>
      <img class="rastreio-logo" :src="logo" alt="Insper" />
    </span>
  </div>
</template>

<script setup lang="ts">
// semnum: o apêndice não numera, como no deck Beamer — continuar a
// contagem da parte principal seria enganoso.
defineProps<{ cont?: string; semnum?: boolean }>();

// Caminho vinculado, não literal: o arquivo em public/insper/ é um link
// simbólico para fora da raiz, e um src literal faria o Vite tentar importá-lo.
const logo = '/insper/logo.png';
</script>

<template>
  <div class="rastreio-band">
    <span class="rastreio-txt"><slot /></span>
    <span class="rastreio-right">
      <span v-if="cont" class="rastreio-cont">{{ cont }}</span>
      <span v-if="!semnum" class="rastreio-num"><SlideCurrentNo /> / <SlidesTotal /></span>
    </span>
  </div>
</template>

<script setup lang="ts">
// semnum: o apêndice não numera, como no deck Beamer — continuar a
// contagem da parte principal seria enganoso.
defineProps<{ cont?: string; semnum?: boolean }>();
</script>

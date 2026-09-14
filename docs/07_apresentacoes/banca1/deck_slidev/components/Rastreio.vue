<template>
  <div class="rastreio-band">
    <span class="rastreio-txt"><slot /></span>
    <span class="rastreio-right">
      <span v-if="cont" class="rastreio-cont">{{ cont }}</span>
      <span class="rastreio-num"><SlideCurrentNo /> / <SlidesTotal /></span>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ cont?: string }>();
</script>

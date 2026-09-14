<template>
  <figure class="fig-box">
    <img :src="src" :alt="alt" :style="{ maxHeight: h }" />
  </figure>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ src: string; alt?: string; h?: string }>(), { h: '18rem', alt: '' });
</script>

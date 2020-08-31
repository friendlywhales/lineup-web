<template>
  <div>
    <div class="" v-if="posts" v-show="isInitialLoaded">
      <posts-grid :posts="posts"></posts-grid>
    </div>
    <div v-else>
      없다.
    </div>

    <div v-show="!isInfiniteLoaded">
      무한 스크롤용 로딩 ui
    </div>
  </div>
</template>

<script lang="ts">
import Collection from './scripts/collection';
export default Collection;
</script>

<style lang="scss" scoped>
  @import '@/assets/styles/base.scss';
</style>

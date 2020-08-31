<template>
  <div>
    <loading-spinner v-if="isLoading"></loading-spinner>
    <div class="home"
         v-infinite-scroll="loadMore"
         :infinite-scroll-disabled="isLoadingMore"
         :infinite-scroll-distance="10">
      <post-detail :key="`timeline-${item.uid}`"
                   :prop-post-uid="item.uid"
                   v-for="item in timelinePosts"></post-detail>
      <div class="guide__no-more" v-if="!nextPage && hasEverLoaded">{{ $t('message["더이상 없습니다."]') }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import Home from './scripts/home';
export default Home;
</script>

<style lang="scss" scoped>
  .home {
    height: 100vh;
    overflow-y: auto;
  }

  .guide__no-more {
    padding: 0 20px 40px;
    color: #444;
  }
</style>

<template>
  <div>
    <div v-if="pageName === 'Search'">
      <div :class="['container', {active: currentInputSearchTerm}]">
        <ul class="tag__list" v-if="tags.length > 0">
          <li class="tag__item"
              :key="index"
              v-for="(item, index) in tags"
              @click="viewTagPosts(item.name)">
            <div class="wrapper">
              <span class="tag__term">#{{ item.name }}</span>
              <span class="tag__post-number">게시물 {{ item.post_number }}개</span>
            </div>
          </li>
        </ul>
        <div class="errors__not-exists" v-if="tags.length === 0">검색 결과 없음</div>
      </div>

      <div :class="['container', {active: !currentInputSearchTerm}]">
        <loading-spinner v-if="isLoading"></loading-spinner>
        <div class="cards__container"
             v-infinite-scroll="loadMore"
             :infinite-scroll-disabled="isLoadingMore"
             :infinite-scroll-distance="10">

          <posts-grid :posts.sync="posts"></posts-grid>
          <!--<div class="guide__no-more" v-if="!nextPage && hasEverLoaded">더이상 없습니다.</div>-->
        </div>
      </div>

    </div>

    <router-view v-else-if="pageName === 'SearchResult'"></router-view>
  </div>
</template>

<script lang="ts">
import Search from './scripts/search';
export default Search;
</script>

<style lang="scss" scoped>
.container {
  display: none;

  &.active {
    display: block;
  }
}

.tag__list {
  padding: 10px 20px;
  width: 100%;
  box-sizing: border-box;
  color: #666;

  .tag__item {
    border-bottom: 1px solid #e1e1e1;
    padding: 15px 0 10px;

    .wrapper {
      width: 100%;
      box-sizing: border-box;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      flex-direction: column;
    }

    .tag__term {
      font-weight: bold;
      padding: 3px 0 .5rem;
    }
    .tag__post-number {
      color: #999;
      font-size: 0.875rem;
    }
  }
}
.errors__not-exists {
  padding-top: 198px;
  color: #666;
}

.cards__container {
  height: 100vh;
  overflow-y: auto;
}

.guide__no-more {
  padding: 0 20px 40px;
  color: #444;
}
</style>

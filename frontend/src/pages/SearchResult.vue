<template>
  <div v-if="isLoaded">
    <nav class="navigation-bar navigation-bar__search-result">
      <router-back class="btn search-result__button">
        <i class="fas fa-chevron-left"></i>
      </router-back>
      <figure class="search-result__container">
        <img :src="titleImage" class="search-result__image" v-show="titleImage">
        <figcaption class="search-result__term">#{{ term }}</figcaption>
      </figure>
    </nav>

    <h3 class="search-result__title">검색 결과</h3>

    <posts-grid :posts="posts"></posts-grid>
    <div v-show="posts.length === 0">
      <strong>#{{ term }}</strong>에 연결된 게시물이 없습니다.
    </div>
  </div>
  <div v-else>
    <loading-spinner></loading-spinner>
  </div>
</template>

<script lang="ts">
import SearchResult from './scripts/search-result';
export default SearchResult;
</script>

<style lang="scss" scoped>
@import '../assets/styles/base.scss';

.navigation-bar__search-result {
  position: fixed;
  z-index: 21;
  background-color: #fff;
  box-sizing: border-box;
  padding: 0 10px;
  top: 0;
  left: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  height: 96px;

  .search-result__button {
    position: absolute;
    width: 3rem;
    margin-right: 10px;
    z-index: 21;
    top: 10px;
  }
  .search-result__container {
    width: 100%;
    margin: 0 auto;
    padding: 10px 0;
    box-sizing: border-box;
    height: 80px;

    .search-result__image {
      box-sizing: border-box;
      width: 48px;
      height: 48px;
      @include vendor-prefix(border-radius, 50%);
    }
    .search-result__term {
      font-size: 0.9rem;
      color: #333;
      padding: 10px 5rem 0;
    }
  }
}

.search-result__title {
  font-size: 1.25rem;
  font-weight: bold;
  text-align: left;
  padding: 16px;
  margin-top: 96px;
}
.search_result__list {
  border: 1px solid #f00;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  margin-bottom: 3px;

  &:last-child { margin: 0; }

  .search_result__item {
    flex-basis: 200px;
    width: 200px;
    height: 200px;
    box-sizing: border-box;
    border: 1px solid #00f;
    margin-right: 3px;

    &:last-child { margin: 0; }
  }
}
</style>

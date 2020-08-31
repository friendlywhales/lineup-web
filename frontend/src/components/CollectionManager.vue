<template>
  <div class="collection-manager" @click="closeByBackground" ref="collectionManager">
    <div class="collection-manager__container">
      <div class="select-collection__container" v-show="page === 'select'">
        <nav class="manager-nav">
          <h3 class="manager-nav__title">저장 위치</h3>
          <i class="fas fa-plus button-nav-aside" @click="switchPage('create')"></i>
        </nav>

        <div class="collections__list">
          <figure :class="['collections__item', {'collections__item--active': checkCollectionHasPost(post.uid, item.uid)}]"
                  :key="item.uid"
                  v-for="item in collections"
                  @click="togglePostToCollection(item)">
            <img :src="getTitleImage(item)" class="collections__item-image" v-if="getTitleImage(item)">
            <div class="collections__item-image no-image" v-if="!getTitleImage(item)">
              <i class="far fa-folder icon"></i>
            </div>
            <figcaption class="collections__item-name">{{ item.name }}</figcaption>
          </figure>
        </div>

        <div class="collection__guide" v-if="!collections || collections.length === 0">
          <p class="guide__text">만들어 놓은 컬렉션이 없습니다.</p>
          <p class="guide__text">오른쪽 위 + 기호를 눌러 컬렉션을 추가해 보세요.</p>
        </div>

        <button type="button" class="form__button button__close" @click="close">취소</button>
      </div>

      <div class="create-collection__container" v-show="page === 'create'">
        <nav class="manager-nav">
          <i class="fas fa-chevron-left button-nav-aside" @click="switchPage('select')"></i>
          <h3 class="manager-nav__title">새 컬렉션</h3>
        </nav>

        <form class="create-collection__form" @submit.prevent="submitCreatingCollection">
          <div class="form-control">
            <img :src="titleImageUrl" class="form__collection-image">
          </div>
          <div class="form-control">
            <input type="text" class="form__input" v-model.trim="collectionName">
          </div>
          <div class="form-control">
            <button type="button" class="form__button button__close"
                    v-show="!collectionName"
                    @click="switchPage('select')">취소</button>
            <button type="submit" class="form__button button__submit"
                    v-show="collectionName">완료</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import CollectionManager from './scripts/collection-manager';
export default CollectionManager;
</script>

<style lang="scss" src="@/assets/styles/CollectionManager.scss"></style>

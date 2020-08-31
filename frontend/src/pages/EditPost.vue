<template>
  <div v-if="isPostLoaded">
    <nav class="navigation-bar">
      <span class="btn btn-publish" @click="$router.back()">취소</span>
      <h2 class="">게시물 수정</h2>
      <span class="btn btn-publish" @click="onSubmit">확인</span>
    </nav>

    <div v-if="post" class="post-container">
      <div class="post__header">
        <router-link class="post__user" :to="{name: 'UserProfile', params: {uid: post.user}}">
          <img :src="post.user_image" class="post__user-image" v-if="post.user_image">
          <i class="icon icon-anonymous post__user-image" v-if="!post.user_image"></i>
          <div class="post__username">{{ post.nickname || post.user }}</div>
        </router-link>
      </div>

      <div class="post__images">
        <img :src="post.images[0]" class="post__image-item">
      </div>

      <div class="form__control form__content-wrapper">
        <textarea
          class="form__content"
          v-model="postContent"
          ref="formEditPost"
          placeholder="설명을 작성해주세요"></textarea>
      </div>

    </div>
    <div v-else>
      게시물이 존재하지 않거나 접근할 권한이 없습니다.
    </div>

  </div>
  <div v-else>
    <loading-spinner></loading-spinner>
  </div>
</template>

<script lang="ts">
import EditPost from './scripts/edit-post';
export default EditPost;
</script>

<style src="@/assets/styles/NavigationBar.scss" lang="scss" scoped></style>
<style lang="scss" scoped>
@import '../assets/styles/base.scss';

.post-container {
  padding-bottom: 54px;
}
.post__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.post__user {
  padding: 10px 20px;
  text-align: left;
  display: flex;
  align-items: center;

  .post__user-image {
    width: 30px;
    height: 30px;
    margin-right: 5px;
    @include vendor-prefix(border-radius, 50%);
  }

  .post__username {
    font-size: 0.875rem;
    color: #444;
    font-weight: bold;
  }
}

.post__images {
  width: 100%;

  .post__image-item {
    width: 100%;
  }

}


.post__content {
  text-align: justify;
  padding: 10px 20px;
  font-size: 0.9rem;
  line-height: 1.8;

  & /deep/ .hashtag {
    color: #444;
    font-weight: bold;
  }
  &.post__extra-tags {
    padding: 0 20px;
  }
}

.form__content-wrapper {
  padding: 8px 10px;
}
.form__content {
  width: 100%;
  box-sizing: border-box;
  padding: 16px 20px;
  height: 4rem;
  border: 1px solid #eee;
}

  .button__cancel {
    border: 1px solid #ccc;
    padding: 12px 0;
    @include vendor-prefix(border-radius, 16px);
  }
</style>

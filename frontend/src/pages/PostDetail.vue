<template>
  <div v-if="isPostLoaded" class="">
    <div v-if="post" class="post-container">
      <div class="post__header">
        <router-link class="post__user" :to="{name: 'UserProfile', params: {uid: post.user}}">
          <img :src="post.user_image" class="post__user-image" v-if="post.user_image">
          <i class="icon icon-anonymous post__user-image" v-if="!post.user_image"></i>
          <div class="post__username">{{ post.nickname || post.user }}</div>
        </router-link>

        <div class="post__report" @click="toggleReportPost">
          ...
        </div>
      </div>
      <carousel class="post__images"
                :per-page="1"
                :navigation-enabled="isMultiple"
                :navigation-prev-label="''"
                :navigation-next-label="''"
                :pagination-enabled="isMultiple"
                :pagination-padding="2"
                :pagination-size="5"
      >
        <slide v-for="item in post.images" :key="`${post.uid}-${item}`">
          <img :src="item" class="post__image-item">
        </slide>
      </carousel>

      <div class="social-activities">
        <div class="social-activities__buttons">
          <div class="left__buttons">
            <like class="like" :post="post"></like>
          </div>

          <div class="right__buttons">
              <i :class="['icon', 'icon-bookmark', {active: hasCollectedCurrentPost}]"
                 @click="toggleBookmark"
                 v-if="isLoadedCheckingCollectedPost"></i>
          </div>
        </div>

        <div class="social-users__list" v-if="post.likes.length > 0">
          <div v-if="post.likes.length === 1" class="social-users__item">
            <router-link class="social-users__link" :to="{name: 'UserProfile', params: {uid: post.likes[0]}}">{{ post.likes[0] }}</router-link>
             {{ $t('message["님이 좋아합니다."]') }}
          </div>
          <div v-else-if="post.likes.length === 2" class="social-users__item">
            <router-link class="social-users__link" :to="{name: 'UserProfile', params: {uid: post.likes[0]}}">{{ post.likes[0] }}</router-link>{{ $t('message["님,"]') }}
            <router-link class="social-users__link" :to="{name: 'UserProfile', params: {uid: post.likes[1]}}">{{ post.likes[1] }}</router-link>
             {{ $t('message["님이 좋아합니다."]') }}
          </div>
          <div v-else class="social-users__item more-users">
            <router-link class="social-users__link" :to="{name: 'UserProfile', params: {uid: post.likes[0]}}">{{ post.likes[0] }}</router-link>님
            {{ $t("message['$외 n명이 좋아합니다.']", { number: post.likes.length - 1 }) }}</div>
        </div>
      </div>

      <div class="post__content" v-html="hashtagAppliedContent"></div>
      <div class="post__content post__extra-tags">
        <router-link class="hashtag" :to="{name: 'SearchResult', params: {term: 'line-up'}}">#line-up</router-link>
      </div>

      <comments :post="post"></comments>
    </div>
    <div v-else>
      {{ $t('message["게시물이 존재하지 않습니다."]') }}
    </div>

    <collection-manager class="collection__container"
                        v-if="areCollectionsLoaded && isLoadedCheckingCollectedPost && isVisibleCollectionContainer"
                        v-on:closeCollectionManager="hideCollectionContainer"
                        v-on:updateCollectedCurrentPostStatus="updateCollectedCurrentPostStatus"
                        :post="post">
    </collection-manager>

    <input type="text" class="input__copy-permalink" ref="permalink" :value="permalink">

    <div class="report__container" v-if="isVisibleReportPostContainer">
      <div class="wrapper wrapper__choose-type" v-if="reportStep === 1">
        <ul class="report__list">
          <li class="report__item" v-if="post" @click="copyPermalinkToClipboard">{{ $t('message["링크복사"]') }}</li>
          <li class="report__item" v-if="isMyPost" @click="openEditPost">{{ $t('message["수정"]') }}</li>
          <li class="report__item" v-if="isMyPost" @click="confirmDeletePost">{{ $t('message["삭제"]') }}</li>
          <li class="report__item" @click="report('spam')">{{ $t('message["스팸입니다."]') }}</li>
          <li class="report__item" @click="report('inappropriate')">{{ $t('message["부적절합니다."]') }}</li>
        </ul>
        <div class="button__cancel" @click="toggleReportPost">{{ $t('message["취소"]') }}</div>
      </div>

      <div class="wrapper wrapper__confirm" v-else-if="reportStep === 2">
        <nav class="navigation-bar navigation-bar__default">
          <h1 class="navigation-bar__title">{{ $t('message["신고"]') }}</h1>
          <button type="button" class="" @click="toggleReportPost">{{ $t('message["취소"]') }}</button>
        </nav>
        <div>
          {{ $t('message["해당 게시물을 ["]') }}
          <span v-show="reportKind === 'spam'">{{ $t('message["스팸 게시물"]') }}</span>
          <span v-show="reportKind === 'inappropriate'">{{ $t('message["부적절한 게시물"]') }}</span>
          {{ $t('message["]로 신고할까요?"]') }}
        </div>

        <div class="button button__confirm-report" @click="reportConfirm">{{ $t('message["신고하기"]') }}</div>
      </div>
    </div>

    <v-dialog width="90%" height="auto"></v-dialog>
  </div>
  <div v-else>
    <loading-spinner></loading-spinner>
  </div>
</template>

<script lang="ts">
import PostDetail from './scripts/post-detail';
export default PostDetail;
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

  & /deep/ .VueCarousel-navigation-button {
    transform: translate(0, -50%);
    /*border: 1px solid #eee;*/
    width: 32px;
    height: 32px;
    border: none;
    outline: none;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
    @include vendor-prefix(border-radius, 50px);
    @include vendor-prefix(box-shadow, 0 1px 1px 0 rgba(0, 0, 0, 0.2));
  }
  & /deep/ .VueCarousel-navigation-prev {
    display: none;
    /*left: 12px;*/
    /*background: #fff url("~@/assets/styles/images/icon-caret-left-solid.svg") no-repeat center center;*/
  }
  & /deep/ .VueCarousel-navigation-next {
    display: none;
    /*right: 12px;*/
    /*background: #fff url("~@/assets/styles/images/icon-caret-right-solid.svg") no-repeat center center;*/
  }
}
.post__report {
  font-weight: bold;
  padding: 0 20px;

  @media #{$platform-pc} {
    display: none;
  }
}

.social-activities {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 10px 20px 0;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;

  .social-activities__buttons {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-direction: row;
    width: 100%;
    box-sizing: border-box;

    .left__buttons {
      flex-grow: 1;
    }
    .right__buttons {
      display: flex;
      flex-grow: 1;
      justify-content: flex-end;
    }
  }
  .social-users__list {
    display: flex;
    justify-content: flex-start;
    flex-wrap: wrap;
    padding: 0.5rem 0;
    font-size: 0.875rem;

    .social-users__item {
      display: block;
      text-align: left;
      padding-bottom: 8px;

      &.more-users { margin-left: 0.25rem; }
    }
    .social-users__link {
      color: #444;
    }
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

.collection__container {
  position: fixed;
  z-index: 200;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.icon-bookmark {
  width: 16px !important;
  height: 16px !important;

  @media #{$platform-pc} {
    display: none;
  }
}

.report__container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 200;
  background-color: rgba(0, 0, 0, .5);
  display: flex;
  align-items: flex-end;

  .wrapper {
    width: 100%;
    background-color: #fff;
    padding: 16px 24px;
    @media #{$platform-mobile} {
      padding-bottom: 68px;
    }

    &.wrapper__confirm {
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  }

  .report__list {
    padding-bottom: 10px;

    .report__item {
      border: 1px solid #ccc;
      border-bottom: none;
      padding: 12px 0;
      background-color: rgba(250, 249, 249, 0.95);

      &:first-of-type {
        @include vendor-prefix(border-top-left-radius, 16px);
        @include vendor-prefix(border-top-right-radius, 16px);
      }
      &:last-of-type {
        border-bottom: 1px solid #ccc;
        @include vendor-prefix(border-bottom-left-radius, 16px);
        @include vendor-prefix(border-bottom-right-radius, 16px);
      }
    }
  }
  .button__cancel {
    border: 1px solid #ccc;
    padding: 12px 0;
    @include vendor-prefix(border-radius, 16px);
  }
  .button__confirm-report {
    background-color: #9347a9;
    padding: 12px 0;
    margin-top: 20px;
    text-align: center;
    width: 100%;
    color: #fff;
  }
}
.input__copy-permalink {
  position: absolute;
  left: -10000px;
  top: -100000px;
}
</style>

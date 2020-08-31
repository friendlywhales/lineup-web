<template>
  <div>
    <div class="profile-container" v-if="isProfileLoaded">
      <section class="profile__info">
        <profile-image-component :profile="profile"></profile-image-component>

        <div class="profile__subinfo">
          <div class="profile__figure-username">{{ profile.nickname || profile.username }}
            <span class="profile__figure-copy" @click="copyPermalinkToClipboard">&nbsp;COPY&nbsp;</span>
          </div>

          <div class="social-relationships">
            <div class="social-relationships__item followers">
              <span class="social-relationships__count">{{ profile.follower_count }}</span>
              <span class="social-relationships__label">팔로워</span>
            </div>
            <div class="social-relationships__item followings">
              <span class="social-relationships__count">{{ profile.following_count }}</span>
              <span class="social-relationships__label">팔로잉</span>
            </div>
            <button-follow
              class="button__follow"
              :is-allowed="true"
              :is-following.sync="isFollowing"
              :target-username="username"></button-follow>
          </div>
        </div>
      </section>
      <div
        v-if="!userinfo.has_daily_attendance"
        :class="['button__daily-attendance']"
        @click="checkDailyAttendance"
        >
      </div>
      <nav class="profile-nav">
        <ul class="profile-nav__list">
          <li :class="['profile-nav__item', {active: currentTab === 'posts'}]" @click="switchTab('posts')">My</li>
          <li :class="['profile-nav__item', {active: currentTab === 'collections'}]" @click="switchTab('collections')">컬렉션</li>
          <li class="profile-nav__item" v-if="isVisibleWallet && isMyProfilePage">
            <router-link class="profile-nav__link" :to="{name: 'Wallet'}">지갑</router-link>
          </li>
        </ul>
      </nav>
      <article class="posts-container" v-if="arePostsLoaded" v-show="isPostsTab">
        <posts-grid :posts.sync="postItems"></posts-grid>
        <div v-if="postItems.length === 0">게시한 이미지가 없습니다.</div>
      </article>
      <article v-else>
        <loading-spinner></loading-spinner>
      </article>

      <article class="collections-container" v-if="areCollectionsLoaded" v-show="isCollectionsTab">
        <collections-grid :collections.sync="collections"></collections-grid>
        <div v-if="collections.length === 0">생성한 컬렉션이 없습니다.</div>
      </article>
      <article v-else>
        <loading-spinner></loading-spinner>
      </article>
    </div>
    <div v-else>
      <loading-spinner></loading-spinner>
    </div>
     <input type="text" style="position: absolute;left: -10000px;top: -100000px;" ref="permalink" :value="permalink">
  </div>
</template>

<script lang="ts">
import Profile from './scripts/profile';
export default Profile;
</script>

<style lang="scss" scoped>
 @import '~@/assets/styles/App.scss';
  @import '@/assets/styles/base.scss';

  .profile-container {
  }

  .profile-nav { padding: 10px 0; }
  .profile-nav__list {
    display: flex;
    border-top: 1px solid #e1e1e1;
    border-bottom: 1px solid #e1e1e1;
    color: #666;

    .profile-nav__item {
      align-items: stretch;
      width: 100%;
      flex: 1 0 0;
      padding: 9px 0;

      &:last-child { border: none; }
      &.active { color: #9347a9; }

      .profile-nav__link {
        color: #666;
      }
    }
  }

  .profile__info {
    display: flex;
    padding: 24px 10px;
  }

  .profile__subinfo {
    display: flex;
    width: 100%;
    flex-direction: column;
    justify-content: space-between;
  }

  .profile__figure-username {
    flex: 2 0 0;
    align-items: stretch;
    width: 100%;
    text-align: left;
    font-size: 1.4375rem;
    color: #333;
    font-weight: bold;
  }

  .profile__figure-copy {
    cursor: pointer;
    padding: 5px 0;
    font-size: 0.875rem;
    color: #9347a9;
    display:inline-block; /* default값 inline */
    border:2px solid #9347a9; /* 테두리 */
  }

  .social-relationships {
    padding: 10px 0 5px;
    display: flex;
    justify-content: space-between;

    .social-relationships__item {
      padding-right: 10px;
      display: flex;
      flex-direction: column-reverse;

      .social-relationships__count {
        display: block;
        padding: 5px 0;
        text-align: left;
        font-weight: bold;
        font-size: 1.125rem;
        color: #333;
      }
      .social-relationships__label {
        display: block;
        font-size: 0.875rem;
        color: #666;
        text-align: left;
      }
    }

    .button__follow {
      background-color: #9347a9;
      font-size: 0.75rem;
      color: #fff;
      padding: 10px 26px;
      @include vendor-prefix(border-radius, 50px);
    }
  }
</style>

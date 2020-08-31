<template>
  <div :class="['navigation-bar-container', `page-${pageName.toLowerCase()}`]">
    <nav class="navigation-bar navigation-bar__search" v-show="pageName === 'Search'">
      <form method="GET" class="search-form" @submit.prevent="submitSearchForm">
        <input type="text" class="search-form__input" placeholder="Search"
               @input="debouncedOnInputSearchTerm($event.target.value)">
        <router-back class="btn search-form__button">{{ $t('message["취소"]') }}</router-back>
      </form>
    </nav>

    <nav class="navigation-bar navigation-bar__post-detail" v-show="pageName === 'PostDetail'">
      <router-back class="btn search-result__button">
        <i class="fas fa-chevron-left"></i>
      </router-back>
      <h1 class="navigation-bar__title">{{ $t('message["사진"]') }}</h1>
    </nav>

    <nav class="navigation-bar navigation-bar__notifications" v-show="isChildPageOf('Notifications')">
      <ul class="notification-tabmenu__list">
        <li class="notification-tabmenu__item">
          <router-link
            :to="{name: 'FollowingNotifications'}"
            active-class="notification-tabmenu__link--active" class="notification-tabmenu__link">
            {{ $t('message["팔로잉 소식"]') }}
          </router-link>
        </li>
        <li class="notification-tabmenu__item">
          <router-link
            :to="{name: 'RewardsNotifications'}"
            active-class="notification-tabmenu__link--active" class="notification-tabmenu__link">
            {{ $t('message["보상 소식"]') }}
          </router-link>
        </li>
      </ul>
    </nav>

    <nav class="navigation-bar navigation-bar__profile" v-show="pageName === 'Profile'">
      <form method="GET" class="search-form" @submit.prevent="submitSearchForm">
        <input type="text" class="search-form__input" :placeholder="$t(`message['내 핀 검색']`)" v-model="searchTermFromMines">
      </form>
      <router-link :to="{name: 'Settings'}" class="btn user-settings__button">{{ $t('message["설정"]') }}</router-link>
    </nav>

    <nav class="navigation-bar navigation-bar__post-detail" v-show="pageName === 'CollectionDetail'">
      <router-back class="btn search-result__button">
        <i class="fas fa-chevron-left"></i>
      </router-back>
      <h1 class="navigation-bar__title">{{ collectionName || $t('message["컬렉션"]') }}</h1>
    </nav>

    <nav class="navigation-bar navigation-bar__wallet" v-show="isChildPageOf('Wallet')">
      <router-back class="btn search-result__button">
        <i class="fas fa-chevron-left"></i>
      </router-back>
      <h1 class="navigation-bar__title">{{ $t('message["내 지갑"]') }}</h1>
    </nav>

    <nav class="navigation-bar navigation-bar__settings" v-show="isChildPageOf('Settings')">
      <router-link :to="{name: 'Profile'}" class="btn search-result__button">
        <i class="fas fa-chevron-left"></i>
      </router-link>
      <h1 class="navigation-bar__title">{{ $t('message["설정"]') }}</h1>
    </nav>

    <nav class="navigation-bar navigation-bar__default">
      <h1 class="navigation-bar__logo">{{ $t('message["LINEUP"]') }}</h1>

      <div class="official-twitter">
        <a href="https://twitter.com/lineupsns" class="link" target="_blank"></a>
      </div>

    </nav>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';


@Component({ name: 'navigation-bar' })
export default class NavigationBar extends Vue {
  searchTerm: string = '';
  searchTermFromMines: string = '';

  @Getter('getCollection', { namespace: 'contents' }) getCollection!: Function;
  @Getter('currentInputSearchTerm', { namespace: 'contents' }) currentInputSearchTerm!: string;

  get collectionName(this: any): string {
    if (this.pageName !== 'CollectionDetail') { return ''; }
    const collection = this.getCollection(this.$route.params.uid);
    return collection ? collection.name : '';
  }

  @Mutation('inputSearchTerm', { namespace: 'contents' }) inputSearchTerm: any;

  debouncedOnInputSearchTerm = _.debounce((v: string) => this.onInputSearchTerm(v), 200, {});

  onInputSearchTerm(value: string) {
    this.inputSearchTerm(_.trim(value));
  }
  submitSearchForm() {
    if (!this.searchTerm) return;
    this.$router.push({ name: 'SearchResult', params: { term: this.searchTerm } });
  }
}
</script>

<style src="@/assets/styles/NavigationBar.scss" lang="scss" scoped></style>

<template>
  <nav :class="['tabbar-main', `page-${pageName.toLowerCase()}`]" v-show="!isVisibleUploadPage">
    <ul class="tabbar-main__list">
      <li class="tabbar-main__item">
        <router-link
          :to="{name: 'Home'}"
          active-class="tabbar-main__home-link--active" class="tabbar-main__home-link">
          <i :class="['icon__tabbar', 'icon-home-solid', {active: isChildPageOf('Home')}]"></i>
        </router-link>
      </li>
      <li class="tabbar-main__item">
        <router-link
          :to="{name: 'Search'}"
          active-class="tabbar-main__search-link--active" class="tabbar-main__search-link">
          <i :class="['icon__tabbar', 'icon-magnifier-solid', {active: isChildPageOf('Search')}]"></i>
        </router-link>
      </li>
      <li class="tabbar-main__item">
        <upload-form>
          <i class="icon__tabbar icon-squared-plus icon__upload"></i>
        </upload-form>
      </li>
      <li class="tabbar-main__item">
        <router-link
          :to="{name: 'RewardsNotifications'}"
          active-class="tabbar-main__notification-link--active" class="tabbar-main__notification-link">
          <i :class="['icon__tabbar', 'icon-heart', {active: isChildPageOf('Notifications')}]"></i>
        </router-link>
      </li>
      <li class="tabbar-main__item">
        <router-link
          :to="{name: 'Profile'}"
          active-class="tabbar-main__profile-link--active" class="tabbar-main__profile-link">
          <i :class="['icon__tabbar', 'icon-people-solid', {active: isChildPageOf('Profile')}]"></i>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';

@Component({
  name: 'tabbar-main',
  components: {},
})
export default class TabBarMain extends Vue {
  @Getter('isVisibleUploadPage', { namespace: 'contents' }) isVisibleUploadPage!: boolean;

  get tabbarActivePageName(this: any): string {
    if (this.isChildPageOf('Search')) return 'Search';
    if (this.isChildPageOf('Notifications')) return 'Notifications';
    if (this.isChildPageOf('Profile')) return 'Profile';
    if (this.isChildPageOf('SignUp')) return 'SignUp';
    return 'default';
  }

  @Mutation('toggleUploadPage', { namespace: 'contents' }) toggleUploadPage: any;
}
</script>

<style src="@/assets/styles/TabBarMain.scss" lang="scss" scoped></style>

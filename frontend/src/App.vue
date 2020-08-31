<template>
  <div id="app">

    <header class="header-container">
      <navigation-bar></navigation-bar>
    </header>

    <main :class="['main-container', pageMainContainerClass]">
      <router-view></router-view>
    </main>

    <footer :class="['footer-container', pageFooterContainerClass]">
      <tabbar-main></tabbar-main>
    </footer>

    <upload></upload>

    <div class="guide__desktop-limitation" v-show="isShowedGuideDesktopLimitation">
      <div class="guide__content">
        라인업은 모바일에서만 이용 가능합니다.
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { Action, Getter, Mutation } from 'vuex-class';
import { NoCache } from './utils/components';

@Component({
  name: 'app',
  components: {},
})
export default class App extends Vue {
  isLoadedUserInfo: boolean = false;

  @Getter('isLoggedIn', { namespace: 'auth' }) isLoggedIn!: boolean;
  @Getter('userinfo', { namespace: 'auth' }) userinfo!: any;

  get isShowedGuideDesktopLimitation(this: any): boolean {
    return [
      'TopPage',
      'Notifications',
      'FollowingNotifications',
      'RewardsNotifications',
      'Settings',
      'Login',
      'SignUp',
      'Wallet',
      'EditPost',
    ].indexOf(this.pageName) !== -1;
  }
  get pageMainContainerClass(): string {
    return `main-container-${(this.$route.name || 'default').toLowerCase()}`;
  }
  get pageFooterContainerClass(): string {
    return `footer-container-${(this.$route.name || 'default').toLowerCase()}`;
  }
  @NoCache
  get isVisiblePromotionCodeButton(): boolean {
    return this.isLoggedIn &&
      this.isLoadedUserInfo &&
      this.userinfo.signup_route === 'steem' &&
      !this.userinfo.has_promotion_codes;
  }

  @Action('fetchMyInfo', { namespace: 'auth' }) fetchMyInfo: any;
  @Action('fetchFollowingRelationship', { namespace: 'auth' }) fetchFollowingRelationship: any;
  @Action('fetchUserCollections', { namespace: 'contents' }) fetchUserCollections: any;
  @Action('checkDailyAttendance', { namespace: 'auth' }) checkDailyAttendanceAction: any;

  @Mutation('logout', { namespace: 'auth' }) logout: any;

  async applyUserInfo(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.fetchMyInfo();
      this.fetchFollowingRelationship('followings');
      this.fetchFollowingRelationship('followers');
      this.fetchUserCollections();
      resolve();
    });
  }

  async checkDailyAttendance() {
    if (this.userinfo.has_daily_attendance === true) {
      alert('이미 출석하였습니다.');
      return;
    }
    if (this.userinfo.has_daily_attendance === null) {
      alert('출석할 수 없는 상태입니다.');
      return;
    }
    try {
      await this.checkDailyAttendanceAction();
    } catch (e) {
      await this.fetchMyInfo();
    }
  }

  async created() {
    if (!this.isLoggedIn) {
      this.logout();
      return;
    }
    await this.applyUserInfo().catch((err: any) => {
      this.isLoadedUserInfo = false;
    });
    this.isLoadedUserInfo = true;
  }
  // this.$modal
}
</script>

<style src="./assets/styles/App.scss" lang="scss" scoped></style>
<style src="./assets/styles/icons.scss" lang="scss"></style>
<style src="./assets/styles/reset.scss" lang="scss"></style>
<style src="./assets/styles/modal.scss" lang="scss"></style>

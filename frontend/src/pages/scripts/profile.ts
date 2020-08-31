import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import PostsGrid from '@/components/PostsGrid.vue';
import CollectionsGrid from '@/components/CollectionsGrid.vue';
import ProfileImageComponent from '@/components/ProfileImage.vue';
import { NoCache } from '../../utils/components';
import * as T from '../../store/auth/types';
import * as cT from '../../store/contents/types';
import { serviceHost } from '@/api';

const namespace = 'auth';

@Component({
  name: 'profile',
  components: {
    PostsGrid,
    CollectionsGrid,
    ProfileImageComponent,
  },
})
export default class Profile extends Vue {
  currentTab: string = 'posts';
  isProfileLoaded: boolean = false;
  arePostsLoaded: boolean = false;
  areCollectionsLoaded: boolean = false;
  isVisibleReportPostContainer: boolean = false;

  @Action('fetchCollectionPosts', { namespace: 'contents' }) fetchCollectionPosts: any;

  @Getter('userinfo', { namespace }) userinfo!: T.User | T.AnonymouseUser;
  @Getter('username', { namespace }) currentUsername!: string | null;
  @Getter('isFollowingUser', { namespace }) isFollowingUser!: Function;
  @Getter('getProfile', { namespace }) getProfile!: Function;
  @Getter('getProfilePosts', { namespace: 'contents' }) getProfilePosts!: Function;
  @Getter('getUserCollections', { namespace: 'contents' }) getUserCollections!: Function;

  @Mutation('logout', { namespace: 'auth' }) logout: any;

  @NoCache
  get isFollowing(): boolean {
    return this.isFollowingUser(this.username);
  }
  get isPostsTab(): boolean {
    return this.currentTab === 'posts';
  }
  get isCollectionsTab(): boolean {
    return this.currentTab === 'collections';
  }
  @NoCache
  get profile(): T.Profile | null {
    return this.getProfile(this.username) || null;
  }
  @NoCache
  get posts(): any {
    return this.getProfilePosts(this.username);
  }
  get postItems(): cT.Post[] {
    return this.posts ? this.posts.items : [];
  }
  @NoCache
  get username(): string | null {
    if (this.$route.params.uid) {
      return this.$route.params.uid;
    }
    return this.currentUsername || null;
  }
  @NoCache
  get collections(): cT.ICollection[] {
    return this.getUserCollections(this.username);
  }
  get isVisibleWallet(): boolean {
    return this.userinfo.level === 'regular' || this.userinfo.level === 'author';
  }
  get isMyProfilePage(): boolean {
    if (!this.username || !this.profile) { return false; }
    return this.username === this.profile.username;
  }

  @Action('fetchMyInfo', { namespace }) fetchMyInfo: any;
  @Action('fetchFollowingRelationship', { namespace }) fetchFollowingRelationship: any;
  @Action('fetchProfileInfo', { namespace }) fetchProfileInfo: any;
  @Action('fetchProfilePosts', { namespace: 'contents' }) fetchProfilePosts: any;
  @Action('fetchUserCollections', { namespace: 'contents' }) fetchUserCollections: any;
  @Action('checkDailyAttendance', { namespace: 'auth' }) checkDailyAttendanceAction: any;

  switchTab(name: string) {
    this.currentTab = name;
  }
  fetchPosts() {
    this.arePostsLoaded = false;
    this.fetchProfilePosts({
      username: this.username,
      next: this.posts ? this.posts.next : undefined,
    })
      .then((res: any) => {
        this.arePostsLoaded = true;
      });
  }
  fetchCollections() {
    this.areCollectionsLoaded = false;
    this.fetchUserCollections(this.username).then((res: cT.ICollection[]) => {
      this.areCollectionsLoaded = true;

      _.forEach(res, (item) => {
        this.fetchCollectionPosts(item.uid);
      });
    });
  }
  created() {
    if (!this.username) {
      this.logout();
      this.$router.replace({ name: 'Login' });
      return;
    }
    this.isProfileLoaded = false;
    if (this.profile) {
      this.isProfileLoaded = true;
      try {
        this.fetchPosts();
        this.fetchCollections();
      } catch (e) {}
      return;
    }
    this.fetchProfileInfo(this.username)
      .then((res: any) => {
        this.isProfileLoaded = true;
      });
    try {
      this.fetchPosts();
      this.fetchCollections();
    } catch (e) {}
  }

  //출석체크
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
  
  //Mypage 링크복사
  get permalink() {
    return `${serviceHost}/profiles/${this.username}`;
  }

  copyPermalinkToClipboard(this: any) {
    this.isVisibleReportPostContainer = false;
    const el = (this.$refs as any).permalink as HTMLInputElement;

    if (this.isiOS) {
      const oldContentEditable = el.contentEditable;
      const oldReadOnly = el.readOnly;
      const range = document.createRange();

      el.contentEditable = 'true';
      el.readOnly = true;
      range.selectNodeContents(el);

      const s = window.getSelection();
      s.removeAllRanges();
      s.addRange(range);

      el.setSelectionRange(0, 999999);

      el.contentEditable = oldContentEditable;
      el.readOnly = oldReadOnly;
    } else {
      el.select();
    }
    document.execCommand('copy');
    alert('포스트 주소를 복사하였습니다.');
  }
}

import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import { Carousel, Slide } from 'vue-carousel';
import { serviceHost } from '@/api';
import Like from '@/components/Like.vue';
import Comments from '@/components/Comments.vue';
import CollectionManager from '@/components/CollectionManager.vue';
import * as T from '../../store/contents/types';
import { NoCache } from '../../utils/components';

const namespace = 'contents';
// const Pattern = /#([^\u2000-\u206F\u2E00-\u2E7F\s\\'!"#$%&()*+,\-.\/:;<=>?@\[\]^_`{|}~]*)/g;
const PatternHashtag = /#([^\u2000-\u206F\u2E00-\u2E7F\s\\'!"#$%&()*+,.\/:;<=>?@\[\]^_`{|}~]*)/g;

@Component({
  name: 'post-detail',
  components: {
    Like,
    Comments,
    CollectionManager,
    Carousel,
    Slide,
  },
})
export default class PostDetail extends Vue {
  isPostLoaded: boolean = false;
  isVisibleCollectionContainer: boolean = false;
  isVisibleReportPostContainer: boolean = false;
  areCollectionsLoaded: boolean = false;
  isLoadedCheckingCollectedPost: boolean = false;
  hasCollectedCurrentPost: boolean = false;
  reportStep: number = 1;
  reportKind: string = '';

  @Prop({ default: undefined })
  propPostUid!: string | undefined;

  @Getter('getPostByUid', { namespace }) getPostByUid!: Function;
  @Getter('getUserCollections', { namespace }) getUserCollections!: Function;
  @Getter('userinfo', { namespace: 'auth' }) userinfo!: any;

  @Action('fetchPost', { namespace }) fetchPost!: any;
  @Action('fetchUserCollections', { namespace }) fetchUserCollections: any;
  @Action('hasCollectedPost', { namespace }) hasCollectedPost: any;
  @Action('reportPost', { namespace }) reportPost!: any;
  @Action('deletePost', { namespace }) deletePost!: any;

  @NoCache
  get post(): T.Post | null {
    return this.getPostByUid(this.uid) || null;
  }
  @NoCache
  get uid(): string | null {
    return this.propPostUid || this.$route.params.uid;
  }
  @NoCache
  get collections(): T.ICollection[] {
    return this.getUserCollections((this.post as T.Post).user);
  }
  get isMyPost(): boolean {
    if (!this.userinfo || !this.post) { return false; }
    return this.userinfo.isLoggedIn() === true && this.post.user === this.userinfo.username;
  }

  get isMultiple(): boolean {
    return this.post ? this.post.images.length > 1 : false;
  }
  get hashtagAppliedContent(): string {
    if (!this.post || !this.post.content) { return ''; }
    return this.post.content.replace(
      PatternHashtag,
      '<a href="/search/$1" class="hashtag">#$1</a>');
  }
  showCollectionContainer() {
    this.isVisibleCollectionContainer = true;
  }
  hideCollectionContainer() {
    this.isVisibleCollectionContainer = false;
  }
  loadPost() {
    if (this.getPostByUid(this.uid)) {
      this.isPostLoaded = true;
      return new Promise((resolve, reject) => {
        resolve();
      });
    }
    this.isPostLoaded = false;
    return this.fetchPost(this.uid).then((res: T.Post) => {
      this.isPostLoaded = true;
      return res;
    });
  }
  toggleBookmark() {
    if (document.body.clientWidth > 480) {
      // todo: 임시 코드.
      return;
    }
    this.showCollectionContainer();
  }
  toggleReportPost() {
    if (document.body.clientWidth > 480) {
      // todo: 임시 코드.
      return;
    }
    this.isVisibleReportPostContainer = !this.isVisibleReportPostContainer;
    this.reportStep = 1;
  }
  report(kind: string) {
    this.reportKind = kind;
    this.reportStep = 2;
  }
  reportConfirm() {
    if (!this.post) { return; }
    this.reportPost({
      uid: this.post.uid,
      payload: {
        kind: this.reportKind,
      },
    }).then((res: boolean) => {
      if (res) {
        this.reportModal(
          '이 게시물을 신고해 주셔서 감사합니다!',
          '회원님의 소중한 의견은 LINEUP 커뮤니티를 안전하게 유지하는데 도움이 됩니다.',
        );
      } else {
        this.reportModal(
          '게시물 신고가 처리되지 않았습니다.',
          '잠시 후 다시 시도해 보시거나 문제가 지속될 경우 운영자에게 제보해주시기 바랍니다.',
        );
      }
    });
  }
  reportModal(title: string, text: string) {
    this.$modal.show('dialog', {
      title,
      text,
      buttons: [
        {
          title: '확인',
          handler: () => {
            this.$modal.hide('dialog');
            this.toggleReportPost();
          },
        },
      ],
    });
  }
  fetchCollections(user?: string) {
    this.areCollectionsLoaded = false;
    this.fetchUserCollections(user).then((res: any) => {
      this.areCollectionsLoaded = true;
    });
  }
  updateCollectedCurrentPostStatus(status: boolean) {
    this.hasCollectedCurrentPost = status;
  }
  checkingCollectedPost() {
    this.isLoadedCheckingCollectedPost = false;
    if (!this.post) { return; }
    this.hasCollectedPost((this.post as T.Post).uid).then((res: boolean) => {
      this.isLoadedCheckingCollectedPost = true;
      this.hasCollectedCurrentPost = res;
    });
  }

  checkPermission() {
    const user = this.userinfo;
    const post = this.post as T.Post;
    if (!user || !user.isLoggedIn() || user.username !== post.user) {
      alert('권한이 없습니다.');
      return false;
    }
    return true;
  }

  checkPostPeriod() {
    switch ((this.post as T.Post).restrict_code) {
      case null:
        return true;

      case 'over-period':
        alert('7일 이상 된 게시물은 수정 및 삭제가 불가능합니다.');
        return false;

      default:
        alert('내부 정책으로 수정 및 삭제할 수 없습니다.');
        return false;
    }
  }

  async confirmDeletePost(this: any) {
    if (!this.post) {
      alert(this.$t('message["게시물이 존재하지 않거나 아직 읽어들이는 중입니다."]'));
      return;
    }
    if (!this.checkPermission() || !this.checkPostPeriod()) {
      return;
    }
    if (!confirm(this.$t('message["게시물을 삭제하시겠어요?"]'))) {
      return;
    }
    const uid = this.post.uid;
    await this.deletePost({ uid, username: this.post.user });
    this.isVisibleReportPostContainer = false;
    this.$emit('deletedPost', uid);
    if (!this.propPostUid && this.$route.params.uid) {
      this.$router.push({ name: 'Profile' });
    }
  }

  openEditPost() {
    this.$router.push({ name: 'EditPost', params: { uid: this.uid as string } });
  }

  get permalink() {
    return `${serviceHost}/p/${(this.post as T.Post).uid}`;
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

  async created() {
    await this.loadPost()
      .catch((e: any) => {
        this.isPostLoaded = true;
      });
    this.isPostLoaded = true;
    try {
      await this.fetchCollections();
    } catch (e) {}
    this.checkingCollectedPost();
  }
}

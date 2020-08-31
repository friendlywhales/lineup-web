import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import { Carousel, Slide } from 'vue-carousel';
import Like from '@/components/Like.vue';
import Comments from '@/components/Comments.vue';
import CollectionManager from '@/components/CollectionManager.vue';
import * as T from '../../store/contents/types';
import { NoCache } from '../../utils/components';

const namespace = 'contents';
// const Pattern = /#([^\u2000-\u206F\u2E00-\u2E7F\s\\'!"#$%&()*+,\-.\/:;<=>?@\[\]^_`{|}~]*)/g;
const PatternHashtag = /#([^\u2000-\u206F\u2E00-\u2E7F\s\\'!"#$%&()*+,.\/:;<=>?@\[\]^_`{|}~]*)/g;

@Component({
  name: 'edit-post',
  components: {
    Like,
    Comments,
    CollectionManager,
    Carousel,
    Slide,
  },
})
export default class EditPost extends Vue {
  isPostLoaded: boolean = false;
  postContent: string = '';

  @Prop({ default: undefined })
  propPostUid!: string | undefined;

  @Getter('getPostByUid', { namespace }) getPostByUid!: Function;
  @Getter('userinfo', { namespace: 'auth' }) userinfo!: any;

  @Action('fetchPost', { namespace }) fetchPost!: any;
  @Action('patchPost', { namespace }) patchPost: any;
  @Action('fetchMyInfo', { namespace: 'auth' }) fetchMyInfo: any;

  @NoCache
  get post(): T.Post | null {
    return this.getPostByUid(this.uid);
  }
  @NoCache
  get uid(): string | null {
    return this.propPostUid || this.$route.params.uid;
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

  async onSubmit() {
    const uid = (this.post as T.Post).uid;
    await this.patchPost({
      uid,
      data: {
        content: this.postContent,
      },
    });
    await this.fetchPost(uid);
    this.$router.push({ name: 'PostDetail', params: { uid } });
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

  async created() {
    await this.fetchMyInfo();
    await this.loadPost()
      .catch((e: any) => {
        this.isPostLoaded = true;
      });

    if (!this.post) {
      alert('게시물이 존재하지 않거나 잘못된 접근입니다.');
      return;
    }
    if (!this.checkPermission() || !this.checkPostPeriod()) {
      this.$router.back();
      return;
    }

    this.postContent = (this.post as T.Post).orig_content as string;
    this.$nextTick(() => {
      (this.$refs.formEditPost as HTMLTextAreaElement).focus();
    });
  }
}

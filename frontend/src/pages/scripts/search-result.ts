import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { NoCache } from '@/utils/components';
import * as T from '@/store/contents/types';
import PostsGrid from '@/components/PostsGrid.vue';

const namespace = 'contents';

@Component({
  name: 'search-result',
  components: {
    PostsGrid,
  },
})
export default class SearchResult extends Vue {
  isLoaded: boolean = false;
  posts: T.IPost[] = [];

  @Action('fetchTagPosts', { namespace }) fetchTagPosts!: any;

  @NoCache
  get term(): string {
    return this.$route.params.term || '';
  }
  @NoCache
  get titleImage(): string {
    if (this.posts.length === 0) { return ''; }
    return this.posts[0].thumbnails.length > 0
      ? this.posts[0].thumbnails[0].url
      : this.posts[0].images[0];
  }

  created() {
    if (!this.term) {
      this.isLoaded = true;
      return;
    }
    this.isLoaded = false;
    this.posts = [];

    this.fetchTagPosts(this.term)
      .then((res: T.IPost[]) => {
        this.isLoaded = true;
        this.posts = res;
      })
      .catch((err: any ) => {
        this.isLoaded = true;
        this.posts = [];
      });
  }
}

import * as _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Watch } from 'vue-property-decorator';
import * as T from '@/store/contents/types';
import PostsGrid from '@/components/PostsGrid.vue';

const namespace = 'contents';

@Component({
  name: 'search',
  components: {
    PostsGrid,
  },
})
export default class Search extends Vue {
  tags: T.ITag[] = [];
  posts: T.Post[] = [];
  isLoading: boolean = true;
  isLoadingMore: boolean = true;
  nextPage: string | null = null;
  hasEverLoaded: boolean = false;

  @Getter('currentInputSearchTerm', { namespace }) currentInputSearchTerm!: string;

  @Action('fetchTags', { namespace }) fetchTags!: any;
  @Action('fetchSearchAllPosts', { namespace }) fetchSearchAllPosts!: any;

  async loadMore() {
    if (!this.nextPage || this.isLoadingMore || this.currentInputSearchTerm) { return; }
    await this.fetchPosts();
  }

  @Watch('currentInputSearchTerm')
  async onSearch(val: string, oldVal: string) {
    if (!val) { return; }
    this.tags = await this.fetchTags(val);
  }

  viewTagPosts(term: string) {
    this.$router.push({ name: 'SearchResult', params: { term } });
  }

  async fetchPosts() {
    this.isLoading = true;
    this.isLoadingMore = true;
    const res = await this.fetchSearchAllPosts(this.nextPage);
    this.isLoading = false;
    this.isLoadingMore = false;
    this.nextPage = res.next;

    _.forEach(res.results, (item) => {
      const index = _.findIndex(this.posts, { uid: item.uid });
      if (index === -1) {
        this.posts.push(item);
      } else {
        this.posts[index] = item;
      }
    });
  }

  async created() {
    await this.fetchPosts();
    this.hasEverLoaded = true;
  }
}

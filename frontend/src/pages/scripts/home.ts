import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import PostDetail from '../PostDetail.vue';
import * as cT from '../../store/contents/types';
import { NoCache } from '../../utils/components';

@Component({
  name: 'home',
  components: {
    PostDetail,
  },
})
export default class Home extends Vue {
  isLoading: boolean = true;
  isLoadingMore: boolean = true;
  nextPage: string | null = null;
  hasEverLoaded: boolean = false;

  @NoCache
  @Getter('timelinePosts', { namespace: 'contents' }) timelinePosts!: cT.Post[];

  @Action('fetchTimeline', { namespace: 'contents' }) fetchTimeline: any;

  async loadMore() {
    if (!this.nextPage || this.isLoadingMore) { return; }
    await this.loadTimeline();
  }
  async loadTimeline() {
    this.isLoading = true;
    this.isLoadingMore = true;
    const res = await this.fetchTimeline(this.nextPage || undefined) as cT.IPaginatedTimeline;
    this.isLoading = false;
    this.isLoadingMore = false;
    this.nextPage = res.next;
  }

  async created() {
    await this.loadTimeline();
    this.hasEverLoaded = true;
  }
  mounted() {
    this.isLoadingMore = false;
  }
}

import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import * as T from '@/store/contents/types';
import { NoCache } from '@/utils/components';
import PostsGrid from '@/components/PostsGrid.vue';


const namespace = 'contents';

@Component({
  name: 'collection',
  components: {
    PostsGrid,
  },
})
export default class Collection extends Vue {
  isInitialLoaded: boolean = false;
  isInfiniteLoaded: boolean = false;

  @Action('fetchCollectionPosts', { namespace }) fetchCollectionPosts: any;

  @Getter('getCollectionPosts', { namespace }) getCollectionPosts!: Function;

  get uid(): string {
    return this.$route.params.uid;
  }
  @NoCache
  get posts(): T.IPost[] {
    return this.getCollectionPosts(this.uid);
  }

  fetchPosts(): Promise<void> {
    this.isInfiniteLoaded = false;
    return this.fetchCollectionPosts(this.uid)
      .then((res: any) => {
        this.isInfiniteLoaded = true;
      });
  }
  created() {
    this.isInitialLoaded = false;
    this.fetchPosts().then((res: any) => {
      this.isInitialLoaded = true;
    });
  }
}

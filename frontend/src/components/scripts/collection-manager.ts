import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import Like from '@/components/Like.vue';
import Comments from '@/components/Comments.vue';
import * as T from '../../store/contents/types';
import { NoCache } from '../../utils/components';

const namespace = 'contents';

@Component({
  name: 'collection-manager',
  components: {
    Like,
    Comments,
  },
})
export default class CollectionManager extends Vue {
  page: string = 'select';
  collectionName: string = '';

  @Prop()
  post!: T.Post;

  @Getter('getPostByUid', { namespace }) getPostByUid!: Function;
  @Getter('getUserCollections', { namespace }) getUserCollections!: Function;

  @Getter('hasCollectionPost', { namespace }) hasCollectionPost!: Function;

  @Action('createCollection', { namespace }) createCollection!: any;
  @Action('addPostToCollection', { namespace }) addPostToCollection!: any;
  @Action('removePostToCollection', { namespace }) removePostToCollection: any;
  @Action('fetchUserCollections', { namespace }) fetchUserCollections: any;

  @NoCache
  get collections(): T.ICollection[] {
    return this.getUserCollections((this.post as T.Post).user);
  }
  get titleImageUrl(): string {
    return this.post.thumbnails.length > 0 ? this.post.thumbnails[0].url : this.post.images[0];
  }

  checkCollectionHasPost(postUid: string, collectionUid: string): boolean {
    return this.hasCollectionPost(postUid, collectionUid);
  }
  getTitleImage(item: T.ICollection): string | undefined {
    // todo: srcset 필요.
    if (item.title_images.length > 0) return item.title_images[0];
    return undefined;
  }
  switchPage(pagename: string) {
    this.page = pagename;
  }
  close() {
    this.$emit('closeCollectionManager');
  }
  closeByBackground($event?: any) {
    if (!$event || $event.target === this.$refs.collectionManager) {
      this.$emit('closeCollectionManager');
    }
  }
  togglePostToCollection(collection: T.ICollection) {
    if (this.hasCollectionPost(this.post.uid, collection.uid)) {
      this.removePostToExistCollection(collection);
    } else {
      this.addPostToExistCollection(collection);
    }
  }
  removePostToExistCollection(collection: T.ICollection) {
    this.removePostToCollection({ post: this.post, collection })
      .then((res: boolean) => {
        this.$emit('updateCollectedCurrentPostStatus', false);
        // this.hasCollectedCurrentPost = false;
        this.fetchUserCollections().then((res: any) => {
          this.close();
        });
      });
  }
  addPostToExistCollection(collection: T.ICollection) {
    this.addPostToCollection({
      post: this.post,
      collection,
    }).then((res: any) => {
      this.fetchUserCollections().then((res: any) => {
        this.$emit('updateCollectedCurrentPostStatus', true);
        this.close();
      });
    });
  }
  async submitCreatingCollection() {
    const collection = await this.createCollection(this.collectionName);
    await this.addPostToCollection({
      post: this.post,
      collection,
    });
    this.close();
  }
  created() {
  }
}

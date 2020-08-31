<template>
  <div class="posts-grid__item">
    <router-link class="posts-grid__link" :to="{name: 'PostDetail', params: {uid: post.uid}}">
      <img :src="thumbnail" class="posts-grid__image">
    </router-link>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop, Watch } from 'vue-property-decorator';
import { NoCache } from '@/utils/components';
import * as cT from '@/store/contents/types';
import * as _ from 'lodash';

const namespace = 'contents';

@Component({ name: 'each-post-grid' })
export default class EachPostGrid extends Vue {
  @Prop()
  post!: cT.Post;

  get thumbnail(): string {
    return _.get(this.post, 'thumbnails', []).length > 0 ? this.post.thumbnails[0].url : this.post.images[0];
  }
  get postUrl(): string {
    return this.post.uid;
  }
}
</script>

<style lang="scss" scoped>
.posts-grid__item {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.posts-grid__link {
  display: block;
  position: relative;
}
.posts-grid__image {
  display: block;
  width: 100%;
  height: 100%;
}
.posts-grid__collection-name {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  color: #fff;
  font-size: 0.875rem;
  text-align: center;
  padding: 5px 0;
  background-color: rgba(109, 49, 126, .9);
}
</style>

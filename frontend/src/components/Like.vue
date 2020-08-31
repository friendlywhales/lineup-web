<template>
  <div class="like-container" @click="toggle">
    <i :class="['icon', 'icon-heart', {active: hasLiked}]"></i>
    <span class="numbers" v-show="post.likes.length">{{ post.likes.length }}</span>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import * as T from '@/store/contents/types';


const namespace = 'contents';

@Component({ name: 'like' })
export default class Like extends Vue {
  @Prop()
  post!: T.Post;

  hasLiked: boolean = false;

  @Getter('userinfo', { namespace: 'auth' }) userinfo!: any;

  @Action('toggleLike', { namespace }) toggleLike!: any;

  checkHasLiked() {
    this.hasLiked = this.post.likes.indexOf(this.userinfo.username) !== -1;
  }
  toggle() {
    if (document.body.clientWidth > 480) {
      // todo: 임시 코드.
      return;
    }
    this.toggleLike(this.post.uid).then(() => {
      this.checkHasLiked();
    });
  }
  created() {
    this.checkHasLiked();
  }
}
</script>

<style lang="scss" scoped>
.like-container {
  cursor: pointer;
  display: flex;
  align-items: center;

  .numbers {
    font-size: 0.9rem;
    color: #666;
    margin-left: 0.5rem;
  }
}
</style>

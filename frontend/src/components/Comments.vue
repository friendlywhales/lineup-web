<template>
  <div class="comments-container">
    <div class="comments__number" v-if="post && post.comments && post.comments.length > 0">댓글 {{ post.comments.length }}개</div>
    <ul class="comments__list" v-if="post && post.comments">
      <li class="comments__item" :key="item.uid" v-for="item in comments">
        <router-link :to="{name: 'UserProfile', params: {uid: item.user}}" class="username">{{ item.nickname ? item.nickname : item.user }}</router-link>
        {{ item.content }}
      </li>
    </ul>
    <form method="POST" @submit.prevent="submit" class="comment__form">
      <input type="text" class="form__input" placeholder="Add a comment..."
             v-model="content"
             :disabled="isSubmitting">
      <button type="submit" class="form__submit" :disabled="isSubmitting">Post</button>
    </form>
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

@Component({ name: 'comments' })
export default class Comments extends Vue {
  content: string = '';
  isSubmitting: boolean = false;

  @Prop()
  post!: T.Post;

  hasLiked: boolean = false;

  @Getter('userinfo', { namespace: 'auth' }) userinfo!: any;
  @Getter('getComments', { namespace }) getComments!: Function;
  get comments() {
    return this.getComments(this.post.uid);
  }

  @Action('postComment', { namespace }) postComment!: any;

  submit() {
    if (document.body.clientWidth > 480) {
      // todo: 임시 코드.
      return;
    }
    if (this.isSubmitting) return;
    this.isSubmitting = true;
    this.postComment({
      uid: this.post.uid,
      content: this.content,
    }).then((res: any) => {
      this.content = '';
      this.isSubmitting = false;
    }).catch((err: any) => {
      this.isSubmitting = false;
    });
  }
  created() {
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.comments-container {
  display: flex;
  align-items: center;
  flex-direction: column;
}
  .comments__number {
    color: #888;
    font-size: 0.75rem;
    padding: 0 0 8px 20px;
    text-align: left;
    margin: 0 auto 0 0;
  }
  .comments__list {
    width: 100%;
    padding: 0 20px 20px;
    box-sizing: border-box;

    .comments__item {
      font-size: 0.8rem;
      padding: 3px 0 0 0;
      text-align: left;
      line-height: 1.2rem;

      .username {
        display: inline-block;
        font-weight: bold;
        margin-right: 5px;
        color: #444;
      }
    }
  }

  .comment__form {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    padding: 0 15px;

    @media #{$platform-pc} {
      display: none;
    }

    .form__input {
      border: 1px solid #ccc;
      border-right: none;
      width: 100%;
      padding: 10px 20px 10px;
      box-sizing: border-box;

      &:focus {
        @include vendor-prefix(outline, 0);
      }
      @include vendor-prefix(border-top-left-radius, 50px);
      @include vendor-prefix(border-bottom-left-radius, 50px);
      @include placeholder {
        color: #888;
        font-size: 0.875rem;
        padding: 0;
      }
    }
    .form__submit {
      border: 1px solid #ccc;
      border-left: none;
      background-color: transparent;
      color: #c1aac7;
      font-weight: bold;
      padding: 10px 20px 10px;
      margin-left: 0;
      @include vendor-prefix(border-top-right-radius, 50px);
      @include vendor-prefix(border-bottom-right-radius, 50px);
    }
  }
</style>

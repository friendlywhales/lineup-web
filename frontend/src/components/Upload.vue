<template>
  <div class="upload__container" v-if="isVisible">
    <nav class="navigation-bar">
      <i class="fas fa-chevron-left" @click="closePage"></i>
      <h2 class="navigation-bar__logo">이미지 올리기</h2>
      <span class="btn btn-publish" @click="publish">확인</span>
    </nav>

    <form class="editing__form" @submit.prevent="publish">
      <div class="form__control">
        <div class="form__attachment">
          <img class="form__attachment-image" :src="titleAttachmentImage.content" v-if="titleAttachmentImage">
          <i class="far fa-clone form__attachment-number" v-if="attachmentOriginalImageNumber > 1"></i>
        </div>
        <textarea class="form__content" v-model="postContent" placeholder="설명을 작성해주세요"></textarea>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import { NoCache } from '@/utils/components';
import * as T from '@/store/contents/types';

const namespace = 'contents';

@Component({ name: 'upload' })
export default class Upload extends Vue {
  postContent = '';

  @Getter('isVisibleUploadPage', { namespace }) isVisibleUploadPage!: boolean;
  @Getter('draftPost', { namespace }) draftPost!: T.IDraftPost | undefined;

  @Mutation('toggleUploadPage', { namespace }) toggleUploadPage: any;
  @Mutation('removeDraftPost', { namespace }) removeDraftPost: any;
  @Mutation('appendProfilePosts', { namespace }) appendProfilePosts: any;

  @Action('patchPost', { namespace }) patchPost: any;
  @Action('publishPost', { namespace }) publishPost: any;

  @NoCache
  get isVisible(): boolean {
    return !(this.draftPost === undefined);
  }
  @NoCache
  get post() {
    return this.draftPost;
  }
  @NoCache
  get titleAttachmentImage() {
    return this.attachmentImages.length > 0 ? this.attachmentImages[0] : null;
  }
  @NoCache
  get attachmentImages(): T.IAttachment[] {
    return this.post ? this.post.attachments : [];
  }
  @NoCache
  get attachmentOriginalImageNumber(): number {
    return _.filter(this.attachmentImages, { kind: 'original' }).length;
  }

  closePage() {
    this.removeDraftPost();
    this.toggleUploadPage(false);
  }
  resetForm() {
    this.postContent = '';
  }
  async publish() {
    const uid = (this.post as T.IDraftPost).uid;
    await this.patchPost({
      uid,
      data: {
        content: this.postContent,
      },
    });
    const post = await this.publishPost(uid);
    this.appendProfilePosts({
      username: post.user,
      posts: [new T.Post(post)],
      reverse: true,
    });

    this.resetForm();
    this.closePage();
    this.$router.push({ name: 'PostDetail', params: { uid } });
  }
}
</script>

<style lang="scss">
@import '../assets/styles/base.scss';

.upload__container {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 100;
  background-color: #fff;
  width: 100%;
  height: 100%;
}

.navigation-bar {
  width: 100%;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  padding: 10px;
  color: #333;
  font-weight: bold;

  .btn-publish {
    color: #9347a9;
  }
}

.editing__form {
  padding: 15px;
  box-sizing: border-box;

  .form__control {
    display: flex;
    flex: 1 0 0;
    width: 100%;
    height: 100%;
  }
  .form__attachment {
    min-width: 120px;
    min-height: 120px;
    width: 120px;
    height: 120px;
    margin-right: 10px;
    position: relative;

    .form__attachment-image {
      width: 100%;
      height: 100%;
      @include vendor-prefix(border-radius, 4px);
    }
    .form__attachment-number {
      position: absolute;
      right: 5px;
      top: 5px;
      font-weight: bold;
      background-color: #9347a9;
      color: #fff;
      padding: 4px;
      @include vendor-prefix(border-radius, 4px);
    }
  }
  .form__content {
    display: block;
    min-height: 120px;
    width: 100%;
    text-align: left;
    padding: 10px;
    box-sizing: border-box;
    border: 1px solid #e1e1e1;
    color: #888;
    line-height: 1.64;
    font-size: 0.875rem;
    @include vendor-prefix(border-radius, 4px);
    @include placeholder {
      color: #888;
    }
  }
}
</style>

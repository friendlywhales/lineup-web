<template>
  <form class="upload-form"
        @change="changeForm"
        @submit.prevent="() => {}" ref="uploadForm">
    <input type="file"
           accept="image/png,image/jpeg"
           class="button-upload"
           ref="uploadElement"
           @click.stop="callNativePhotoUI"
           multiple>
    <slot class="slot__content"></slot>
  </form>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import * as T from '@/store/contents/types';

const namespace = 'contents';

const nativePhotoUIiOSMinimumVersion = [1, 1, 0];

@Component({ name: 'upload-form' })
export default class UploadForm extends Vue {

  @Getter('isVisibleUploadPage', { namespace }) isVisibleUploadPage!: boolean;

  @Mutation('toggleUploadPage', { namespace }) toggleUploadPage: any;

  @Action('createDraftPost', { namespace }) createDraftPost: any;
  @Action('uploadPostAttachment', { namespace }) uploadPostAttachment: any;

  callNativePhotoUI(this: any, e: Event) {
    const token = localStorage.getItem('token');

    if (!token) {
      e.preventDefault();
      alert(this.$t('message["로그인 후 업로드 가능합니다."]'));
      return false;
    }
    if (this.isiOS && this.isGreaterAppVersion(nativePhotoUIiOSMinimumVersion)) {
      e.preventDefault();
      window.location.href = `lineup://post?token=${token}`;
      return false;
    }
    return true;
  }

  isGreaterAppVersion(version: number[]): boolean {
    const appVersion = localStorage.getItem('appVersion');
    if (!appVersion) { return false; }
    const parts = appVersion.split('.');

    if (+parts[0] < version[0]) { return false; }
    if (+parts[1] < version[1]) { return false; }
    if (+parts[2] < version[2]) { return false; }
    return true;
  }

  async changeForm() {
    const post = await this.createDraftPost()
      .catch((err: any) => {
        elForm.reset();
        alert('권한이 없거나 게시물 생성 요청을 실패하였습니다.');
        return;
      });

    const formdata = new FormData();
    const el = (this.$refs.uploadElement as any);
    const elForm = (this.$refs.uploadForm as any);
    if (!el.files || el.files.length === 0) {
      return;
    }

    _.forEach(el.files, (o, i) => {
      formdata.append('order', (i + 1).toString());
      formdata.append('content', o);
    });
    try {
      await this.uploadPostAttachment({ uid: post.uid, formdata });
      this.toggleUploadPage(true);
      elForm.reset();
    } catch (err) {
      this.toggleUploadPage(false);
      elForm.reset();
      alert('크기가 500*500 미만이거나 포맷에 문제가 있는 이미지는 업로드 할 수 없습니다.');
    }
  }
}
</script>

<style lang="scss">
  .upload-form {
    position: relative;

    .button-upload {
      opacity: 0;
      position: absolute;
      width: 100%;
      border: 1px solid #f00;
      top: 0;
      left: 0;
      z-index: 2;
    }
    .slot__content {
      display: inline-block;
      position: relative;
      z-index: 1;
    }
  }
</style>

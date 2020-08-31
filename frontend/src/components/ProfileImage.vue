<template>
  <div class="profile__figure" :style="{width: computedWidth, height: computedHeight}">
    <img :src="profile.image" class="profile__figure-image" v-if="profile.image">
    <div class="profile__figure-image no-image" v-if="!profile.image"></div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { Prop } from 'vue-property-decorator';
import * as T from '../store/auth/types';

const namespace = 'auth';

@Component({ name: 'profile-image-component' })
export default class ProfileImageComponent extends Vue {
  isProfileLoaded: boolean = false;

  @Prop() profile!: T.Profile[];
  @Prop({ default: '100px' }) width!: string;
  @Prop({ default: '100px' }) height!: string;

  get computedWidth(): string {
    return this.width;
  }
  get computedHeight(): string {
    return this.width;
  }
  async created() {
  }
}
</script>

<style lang="scss" scoped>
  @import '~@/assets/styles/base.scss';

  .profile__figure {
    margin-right: 15px;

    .profile__figure-image {
      @include vendor-prefix(border-radius, 50%);
      min-width: 80px;
      min-height: 80px;
      max-width: 100px;
      max-height: 100px;

      &.no-image {
        background: url("~@/assets/styles/images/icon-anonymous.svg") no-repeat center center;
        background-size: cover;
        width: 100px;
        height: 100px;
      }
    }
  }
</style>

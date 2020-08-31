<template>
  <button type="button" class="btn-follow" @click="toggleFollowing" v-if="isAllowed">
    <slot name="followLabel" v-if="!followingStatus">Follow</slot>
    <slot name="unfollowLabel" v-else>UnFollow</slot>
  </button>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';

const namespace = 'auth';

@Component({ name: 'button-follow' })
export default class ButtonFollow extends Vue {
  @Prop({ default: false })
  isAllowed!: boolean;
  @Prop()
  isFollowing!: boolean;
  @Prop()
  targetUsername!: string;

  followingStatus: boolean = false;

  @Action('toggleFollow', { namespace }) toggleFollow: any;

  toggleFollowing() {
    this.toggleFollow(this.targetUsername)
      .then((res: any) => {
        this.followingStatus = res as boolean;
      })
      .catch((err: any) => {
        if (_.isString(err.response.data)) {
          alert(err.response.data);
        } else if (_.isArray(err.response.data) && err.response.data.length > 0) {
          alert(err.response.data[0]);
        } else {
          alert('팔로잉하지 못했습니다. 이 문제가 계속된다면 contact@line-up.me 로 문의 바랍니다.');
        }
      });
  }

  created() {
    this.followingStatus = this.isFollowing;
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.btn-follow {
  @include vendor-prefix(border-radius, 10px);
  display: block;
  background-color: #b0549f;
  font-size: 0.8rem;
  padding: 2px 12px;
  color: #fff;
  font-weight: bold;
  border: none;
}
</style>

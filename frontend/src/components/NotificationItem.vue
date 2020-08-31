<template>
  <div @click="click(item)">
    <div class="notification__trigger">
      <img src="/static/img/noprofile.png" class="trigger__image">
    </div>
    <div class="notification__content">
      <div class="wrapper">
        <div v-if="item.kind === 'following_new_post'">
          <router-link :to="{name: 'UserProfile', params: {uid: item.trigger}}">{{ item.trigger }}</router-link>
          님이 새로운 게시물을 올렸습니다.
        </div>
        <div v-else-if="item.kind === 'new_vote_user_voted'">
          내가 보팅한 게시물에
          <router-link :to="{name: 'UserProfile', params: {uid: item.trigger}}">{{ item.trigger }}</router-link>
          님도 보팅하였습니다.
        </div>
        <div v-else-if="item.kind === 'new_comment_user_commented'">
          내가 댓글 남긴 게시물에
          <router-link :to="{name: 'UserProfile', params: {uid: item.trigger}}">{{ item.trigger }}</router-link>
          님도 댓글을 남겼습니다.
        </div>
        <div v-else-if="item.kind === 'new_comment_user_posted'">
          내 게시물에
          <router-link :to="{name: 'UserProfile', params: {uid: item.trigger}}">{{ item.trigger }}</router-link>
          님이 댓글을 남겼습니다.
        </div>
        <span class="content__distance-time">{{ distanceInWordsToNow(item.created_at) }}</span>
      </div>

      <div class="content__posts" v-if="titleImage">
        <img :src="titleImage" class="content__thumbnail">
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import * as T from '@/store/messaging/types';

const namespace = 'messaging';

@Component({ name: 'notification-item' })
export default class NotificationItem extends Vue {
  @Prop()
  item!: T.Notification;

  get titleImage() {
    return this.item.thumbnails.length > 0 ? this.item.thumbnails[0].url : '';
  }
  click(item: any) {
    this.$router.push({ name: 'PostDetail', params: { uid: item.content.uid } });
    return false;
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/styles/base.scss';

 .notification__trigger {
  width: 40px;
  height: 40px;
  max-width: 40px;
  max-height: 40px;
  padding-right: 8px;
  flex: 1 0 0;

  .trigger__image {
    @include vendor-prefix(border-radius, 50%);
    width: 100%;
    height: 100%;
    box-sizing: border-box;
  }
}

.notification__content {
  box-sizing: border-box;
  width: 100%;
  flex: 1 0 0;
  text-align: left;
  padding-top: 2px;
  font-size: 0.85rem;

  .wrapper {
    display: flex;
  }

  .content__posts {
    box-sizing: border-box;
    padding: 5px 4px 0;
  }
  .content__thumbnail {
    width: 40px;
    height: 40px;
    padding: 2px;
  }
  .content__distance-time {
    color: rgba(0, 0, 0, .5);
    padding-left: .3rem;
  }
}
</style>

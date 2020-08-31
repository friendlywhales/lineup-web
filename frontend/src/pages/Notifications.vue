<template>
  <div v-show="isLoaded">
    <ul class="notification__list">
      <li class="notification__item"
          :key="item.uid"
          v-for="item in notifications"
          is="notification-item" :item="item"></li>
    </ul>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import NotificationItem from '@/components/NotificationItem.vue';
import { NoCache } from '@/utils/components';
import * as T from '@/store/messaging/types';

const namespace = 'messaging';

@Component({
  name: 'following-notifications',
  components: {
    NotificationItem,
  },
})
export default class FollowingNotifications extends Vue {
  isLoaded: boolean = false;

  @Getter('followingNotifications', { namespace }) followingNotifications!: T.Notification[];
  @Getter('rewardNotifications', { namespace }) rewardNotifications!: T.Notification[];

  @Action('fetchNotifications', { namespace }) fetchNotifications: any;

  @NoCache
  get notifications(this: any): T.Notification[] {
    if (this.pageName === 'FollowingNotifications') {
      return this.followingNotifications;
    }
    if (this.pageName === 'RewardsNotifications') {
      return this.rewardNotifications;
    }
    return [];
  }

  created() {
    this.isLoaded = false;
    this.fetchNotifications().then((res: any) => {
      this.isLoaded = true;
    });
  }
}
</script>

<style lang="scss" scoped>
  .notification__list {
    width: 100%;
    box-sizing: border-box;
    padding: 20px 10px;

    .notification__item {
      width: 100%;
      box-sizing: border-box;
      padding: 5px 0;
      cursor: pointer;
      display: flex;
      align-items: flex-start;
      justify-content: flex-start;
    }
  }
</style>


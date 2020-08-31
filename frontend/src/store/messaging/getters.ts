
import { GetterTree } from 'vuex';
import { IMessagingState } from './state';
import * as T from './types';
import * as rT from '../types';

export default <GetterTree<IMessagingState, rT.IRootState>> {
  followingNotifications(state: IMessagingState): T.Notification[] {
    return state.notifications.following;
  },
  rewardNotifications(state: IMessagingState): T.Notification[] {
    return state.notifications.reward;
  },
};

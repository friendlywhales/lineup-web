
import _ from 'lodash';
import { MutationTree } from 'vuex';
import * as T from './types';
import { IMessagingState } from './state';

export default <MutationTree<IMessagingState>> {
  updateNotifications(state: IMessagingState, items: T.INotification[]) {
    _.forEach(items, (item) => {
      const notification = new T.Notification((item));
      const kind = notification.kind === 'following_new_post' ? 'following' : 'reward';
      if (_.findIndex(state.notifications[kind], { uid: item.uid }) > -1) {
        return;
      }
      state.notifications[kind].push(notification);
    });
  },
};


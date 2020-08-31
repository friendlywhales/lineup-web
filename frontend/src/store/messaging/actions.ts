
import { ActionTree, ActionContext, Store } from 'vuex';
import api, { customHeaders } from '@/api';
import { IMessagingState } from './state';
import * as T from './types';
import { EnumHttpStatus } from '../types';

export default <ActionTree<IMessagingState, any>> {
  async fetchNotifications({ commit }, params?: { next?: string }): Promise<void> {
    const next = params ? params.next || '' : '';
    return api
      .get(`/messaging/notifications/?uid=${next}`)
      .then((res: any) => {
        commit('updateNotifications', res.data.results);
      });
  },
};

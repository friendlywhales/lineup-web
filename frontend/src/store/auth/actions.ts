
import axios, { AxiosResponse } from 'axios';
import _ from 'lodash';
import { ActionTree, ActionContext, Store } from 'vuex';
import { IAuthState } from './state';
import * as T from './types';
import { EnumHttpStatus } from '../types';
import api, { apiHost, apiAuthPath, apiPathPrefix } from '../../api';

export default <ActionTree<IAuthState, any>> {
  async login(this: any, { commit }, authInfo: T.IPasswordForm): Promise<any> {
    return axios
      .post(`${apiHost}${apiAuthPath}`, {
        ...authInfo,
        withCredentials: false,
      })
      .then((res: any) => {
        commit('login', { token: res.data.token, username: authInfo.username });
        return res.data.token;
      })
      .catch((err: any) => {
        return Promise.reject(err);
      });
  },

  async fetchMyInfo({ commit }): Promise<EnumHttpStatus> {
    return api
      .get('/accounts/users/me/')
      .then((res: any) => {
        commit('updateMyInfo', res.data);
        commit('updateUserProfile', res.data);
        return EnumHttpStatus.OK;
      });
  },

  async fetchProfileInfo({ commit }, username: string): Promise<EnumHttpStatus> {
    return api
      .get(`/accounts/profiles/${username}/`)
      .then((res: any) => {
        commit('updateUserProfile', res.data);
        return EnumHttpStatus.OK;
      });
  },

  async toggleFollow({ commit }, username: string): Promise<void | boolean> {
    return api.post(`/accounts/profiles/${username}/follow/`)
      .then((res: any) => {
        const isFollowing = res.status !== 204;
        commit('updateFollowingStatus', {
          kind: 'followings',
          username,
          status: isFollowing,
        });
        return isFollowing;
      });
  },

  async fetchFollowingRelationship({ commit }, kind: string): Promise<void> {
    return api
      .get(`/accounts/users/${kind}/`)
      .then((res: any) => {
        _.forEach(res.data, (item) => {
          commit('updateFollowingStatus', {
            kind,
            username: item.target,
            status: true,
          });
        });
      });
  },

  async fetchLineUpAccessToken({ commit }): Promise<string> {
    return api
      .get('/accounts/users/access-token/')
      .then((res: any) => {
        commit('login', { token: res.data.token, username: res.data.username });
        return res.data.token;
      });
  },

  async signup({ commit }, data: T.SignUpForm): Promise<T.IUser> {
    return axios
      .post(`${apiHost}${apiPathPrefix}/accounts/users/signup/`, data)
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchPromotionCode({ commit }, code: string): Promise<T.PromotionCode> {
    return axios
      .get(`${apiHost}${apiPathPrefix}/operations/promotion-codes/${code}/`)
      .then((res: any) => {
        return res.data;
      });
  },

  async consumePromotionCode({ commit }, code: string): Promise<T.PromotionCode> {
    return api
      .post(`${apiHost}${apiPathPrefix}/operations/promotion-codes/${code}/consume/`)
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchSteemAccountInfo({ commit }, usernames: string[]): Promise<any> {
    const data = {
      jsonrpc: '2.0',
      method: 'call',
      params: [
        'database_api',
        'get_accounts',
        [usernames],
      ],
    };
    return axios.post('https://api.steemit.com', data)
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchSteemDynamicGlobalProperties({ commit }, params?: any[]): Promise<any> {
    const data = {
      id: 1,
      jsonrpc: '2.0',
      method: 'condenser_api.get_dynamic_global_properties',
      params: params || [],
    };
    return axios.post('https://api.steemit.com', data)
      .then((res: any) => {
        return res.data;
      });
  },

  async patchUserinfo({ commit }, params: { uid: string, payload: any}): Promise<any> {
    return api.patch(`/accounts/users/${params.uid}/`, params.payload)
      .then((res: any) => {
        return res.data;
      });
  },

  async connectSocialAuth({ commit }, payload: { token: string, provider: string }): Promise<any> {
    return api
      .post(`${apiHost}${apiPathPrefix}/accounts/users/social-connect/`, payload)
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchSteemConnectAccountInfo({ commit }, token: string): Promise<any> {
    return axios.post(
      'https://steemconnect.com/api/me',
      undefined,
      {
        headers: {
          Authorization: token,
        },
      },
    )
      .then((res: AxiosResponse) => res.data);
  },

  async postProfileImage({ commit }, payload: FormData): Promise<any> {
    return api.post('/accounts/users/profile-image/', payload)
      .then((res: AxiosResponse) => res.data);
  },

  async checkDailyAttendance({ commit }): Promise<any> {
    return api.post('/accounts/users/check-daily-attendance/')
      .then((res: AxiosResponse) => res.data);
  },

  async patchNotificationSettings({ commit }, payload: any): Promise<any> {
    return api.patch('/accounts/users/notification-settings/', payload)
      .then((res: any) => {
        return res.data;
      });
  },

  async checkRecommendedCode({ commit }, code: string) {
    return axios
      .post(
        `${apiHost}${apiPathPrefix}/accounts/users/check-recommended-code/`,
        { recommended_code: code },
      );
  },
};

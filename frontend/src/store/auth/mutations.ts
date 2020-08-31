import _ from 'lodash';
import { MutationTree } from 'vuex';
import api from '@/api';
import * as T from './types';
import { IAuthState } from './state';

export function login(state: IAuthState, params: { token: string, username: string }) {
  localStorage.setItem('token', params.token);
  localStorage.setItem('username', params.username);
  api.client.defaults.headers.common['Authorization'] = `Token ${params.token}`;

  try {
    (window as any).webkit.messageHandlers.loginStatus.postMessage('{"status": true}');
  } catch (e) {}
}

export function logout(state: IAuthState) {
  state.info = T.anonymous;
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('deviceToken');
  localStorage.removeItem('deviceName');
  localStorage.removeItem('isSentDeviceToken');

  try {
    (window as any).webkit.messageHandlers.loginStatus.postMessage('{"status": false}');
  } catch (e) {}
}

export function updateMyInfo(state: IAuthState, user: T.IUser) {
  state.info = new T.User(user);
}

export function updateUserProfile(state: IAuthState, profile: T.IProfile) {
  state.profiles[profile.username] = new T.Profile(profile);
}

export function updateFollowingStatus(state: IAuthState,
                                      params: { kind: string, username: string, status: boolean }) {
  _.get(state, params.kind)[params.username] = params.status;
}

export default <MutationTree<IAuthState>> {
  login,
  logout,
  updateMyInfo,
  updateUserProfile,
  updateFollowingStatus,
};

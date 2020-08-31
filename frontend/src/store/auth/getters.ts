
import _ from 'lodash';
import { Module, GetterTree } from 'vuex';
import { IAuthState } from './state';
import * as T from './types';
import * as rT from '../types';

export function hasAuthToken(): boolean {
  const token = localStorage.getItem('token');
  return _.isString(token);
}

export function isLoggedIn(state: IAuthState): boolean {
  return hasAuthToken();
}

export function userinfo(state: IAuthState): T.IUser {
  return state.info;
}

export function username(state: IAuthState): string | null {
  return state.info.username || localStorage.getItem('username') || null;
}

function isFollowRelationsWithUser(store: any, username: string): boolean {
  if (!_.has(store, username)) {
    store[username] = false;
  }
  return store[username];
}

export function isFollowingUser(state: IAuthState): Function {
  return (username: string): boolean => isFollowRelationsWithUser(state.followings, username);
}

export function isFollowerUser(state: IAuthState): Function {
  return (username: string): boolean => isFollowRelationsWithUser(state.followers, username);
}

export function getProfile(state: IAuthState): Function {
  return (username: string): T.Profile | undefined => state.profiles[username];
}

export default <GetterTree<IAuthState, rT.IRootState>> {
  isLoggedIn,
  userinfo,
  isFollowingUser,
  isFollowerUser,
  getProfile,
  username,
};

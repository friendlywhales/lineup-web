
import { Module } from 'vuex';
import mutations from './mutations';
import actions from './actions';
import getters from './getters';
import state, { IMessagingState } from './state';
import * as T from './types';
import * as rT from '../types';


const namespaced: boolean = true;

export const Store: Module<IMessagingState, rT.IRootState> = {
  namespaced,
  state,
  actions,
  getters,
  mutations,
};

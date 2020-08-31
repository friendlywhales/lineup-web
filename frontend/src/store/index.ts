import Vue from 'vue';
import Vuex from 'vuex';

import * as T from './types';
import { Store as auth } from './auth';
import { Store as contents } from './contents';
import { Store as messaging } from './messaging';

Vue.use(Vuex);

export default new Vuex.Store<T.IRootState>({
  modules: {
    auth,
    contents,
    messaging,
  },
});


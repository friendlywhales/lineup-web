import Vue from 'vue';
import VeeValidate, { Validator } from 'vee-validate';
// import veeLocaleKo from 'vee-validate/dist/locale/ko';
import VueCarousel from 'vue-carousel';
import Raven from 'raven-js';
import RavenVue from 'raven-js/plugins/vue';
import VueAnalytics from 'vue-analytics';
import VModal from 'vue-js-modal';
import InfiniteScroll from 'vue-infinite-scroll';

import { FormatMixin, RouteMixin, UtilMixin } from './utils/mixins';
import NavigationBar from './components/NavigationBar.vue';
import TabBarMain from './components/TabBarMain.vue';
import RouterBack from './components/scripts/router-back';
import ButtonFollow from './components/ButtonFollow.vue';
import Upload from './components/Upload.vue';
import UploadForm from './components/UploadForm.vue';
import LoadingSpinner from './components/LoadingSpinner.vue';

import { i18n } from './i18n-setup';
import './hooks';
import App from './App.vue';
import router from './router';
import store from './store';

Raven
  .config('https://cbf17f698afb42a0b837eb14d3901b6c@sentry.io/1225348')
  .addPlugin(RavenVue, Vue)
  .install();

Vue.config.productionTip = false;

Vue.use(VModal, {
  dialog: true,
  dynamic: true,
  injectModalsContainer: true,
});
Vue.use(InfiniteScroll);
Vue.mixin(FormatMixin);
Vue.mixin(RouteMixin);
Vue.mixin(UtilMixin);
Vue.component('navigation-bar', NavigationBar);
Vue.component('tabbar-main', TabBarMain);
Vue.component('router-back', RouterBack);
Vue.component('button-follow', ButtonFollow);
Vue.component('upload', Upload);
Vue.component('upload-form', UploadForm);
Vue.component('loading-spinner', LoadingSpinner);
Vue.use(VueCarousel);

// Validator.localize('ko', veeLocaleKo);
Vue.use(VeeValidate);
// Vue.use(VeeValidate, {
// locale: 'ko',
  // dictionary: veeLocaleKo,
// });

Vue.use(VueAnalytics, {
  id: 'UA-120921210-1',
  router,
});

// tslint:disable-next-line:no-unused-expression
new Vue({
  el: '#app',
  router,
  store,
  i18n,
  template: '<App/>',
  components: { App },
});

(window as any).updateDeviceToken = (device: string, token: string) => {
  const deviceToken = localStorage.getItem('deviceToken');
  const deviceName = localStorage.getItem('deviceName');

  if (deviceToken === token && deviceName === device) { return; }

  localStorage.setItem('deviceToken', token);
  localStorage.setItem('deviceName', device);
};

(window as any).updateAppVersion = (device: string, version: string) => {
  localStorage.setItem('appVersion', version);
  localStorage.setItem('appDevice', device);
};

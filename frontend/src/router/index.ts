import Vue, { AsyncComponent } from 'vue';
import Router, { RouteConfig, Route, NavigationGuard } from 'vue-router';
import TopPage from '@/pages/TopPage.vue';
import Home from '@/pages/Home.vue';
import Search from '@/pages/Search.vue';
import SearchResult from '@/pages/SearchResult.vue';
import Notifications from '@/pages/Notifications.vue';
import Profile from '@/pages/Profile.vue';
import PostDetail from '@/pages/PostDetail.vue';
import EditPost from '@/pages/EditPost.vue';
import Collection from '@/pages/Collection.vue';
import PromotionCode from '@/pages/PromotionCode.vue';
import Login from '@/pages/Login.vue';
import SignUp from '@/pages/SignUp.vue';
import Wallet from '@/pages/Wallet.vue';
import PageNotFound from '@/pages/PageNotFound.vue';
import ErrorPage from '@/pages/ErrorPage.vue';
import SocialLogin from '../pages/scripts/social-login';
import Settings from '@/pages/Settings.vue';
import OnMaintenance from '@/pages/OnMaintenance.vue';
import api from '../api';

// const HelloWorld: AsyncComponent = (): any => import('@/components/HelloWorld.vue');

Vue.use(Router);

const routes: RouteConfig[] = [
  {
    path: '/',
    name: 'TopPage',
    component: TopPage,
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { requiresAuth: true },
    children: [
      {
        path: ':term',
        name: 'SearchResult',
        component: SearchResult,
      },
    ],
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: { template: '<div><router-view></router-view></div>' },
    meta: { requiresAuth: true },
    children: [
      {
        path: 'followings',
        name: 'FollowingNotifications',
        component: Notifications,
      },
      {
        path: 'rewards',
        name: 'RewardsNotifications',
        component: Notifications,
      },
    ],
  },
  {
    path: '/profiles',
    name: 'Profile',
    component: Profile,
    children: [
      {
        path: ':uid',
        name: 'UserProfile',
        component: Profile,
      },
    ],
  },
  {
    path: '/p',
    name: 'PostList',
    component: { template: '<div><router-view></router-view></div>' },
    children: [
      {
        path: ':uid([a-zA-Z0-9\-]+)/edit',
        name: 'EditPost',
        component: EditPost,
      },
      {
        path: ':uid([a-zA-Z0-9\-]+)',
        name: 'PostDetail',
        component: PostDetail,
      },
    ],
  },
  {
    path: '/collections',
    name: 'CollectionList',
    component: { template: '<div><router-view></router-view></div>' },
    children: [
      {
        path: ':uid',
        name: 'CollectionDetail',
        component: Collection,
      },
    ],
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'promotion-codes',
        name: 'PromotionCode',
        component: PromotionCode,
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
  },
  {
    path: '/social-auth/login/done',
    name: 'SocialLogin',
    component: SocialLogin,
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: Wallet,
    meta: { requiresAuth: true },
  },
  {
    path: '/errors/:type',
    component: ErrorPage,
  },
  {
    path: '*',
    component: PageNotFound,
  },
  // {
  //   path: '*',
  //   component: OnMaintenance,
  // },
];

const router: Router = new Router({
  mode: 'history',
  base: '/',
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    next();
    if (!localStorage.getItem('token')) {
      next({
        name: 'Login',
        query: { redirect: to.fullPath },
      });
    } else {
      next();
    }
  } else {
    next();
  }

  // if (localStorage.getItem('isSentDeviceToken') !== 'true') {
  const deviceToken = localStorage.getItem('deviceToken');
  const deviceName = localStorage.getItem('deviceName');
  if (localStorage.getItem('token') && deviceName && deviceToken) {
    const payload = {
      device: deviceName,
      token: deviceToken,
    };
    api
      .post('/accounts/users/notification-tokens/', payload)
      .then(() => {
        localStorage.setItem('isSentDeviceToken', 'true');
      })
      .catch((err) => { console.log(err); });
  }
  // }
});

export default router;

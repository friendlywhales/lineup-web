import Vue from 'vue';
import Component from 'vue-class-component';
import { Action } from 'vuex-class';
import api from '../../api';

const namespace = 'auth';

@Component({ name: 'social-login' })
export default class SocialLogin extends Vue {
  @Action('connectSocialAuth', { namespace }) connectSocialAuthAction: any;
  @Action('fetchMyInfo', { namespace }) fetchMyInfo: any;

  render() {
    return '<div></div>';
  }

  async connectSocialAuth(payload: { token: string, provider: string }) {
    const res = await this.connectSocialAuthAction(payload);
    localStorage.setItem('token', payload.token);
    localStorage.setItem('username', res.username);
    api.setupClient();
    await this.fetchMyInfo();
    this.$router.replace({ name: 'Settings' });
    return res;
  }

  async created() {
    const token = localStorage.getItem('token');
    const provider = this.$route.query.p as string;

    localStorage.setItem('token', this.$route.query.t);
    localStorage.setItem('username', this.$route.query.u);
    
    api.setupClient();
    if (!!token && !!this.$route.query.t && !!this.$route.query.u && !!provider) {
      await this.connectSocialAuth({ token, provider });
      return;
    }
    this.$router.replace({ name: 'Home' });
  }
}

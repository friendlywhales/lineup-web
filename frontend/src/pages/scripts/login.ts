import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';
import { socialLoginBaseUrl } from '../../api';

const namespace = 'auth';

@Component({ name: 'login' })
export default class Login extends Vue {
  username: string = '';
  password: string = '';
  rememberMe: boolean = false;
  formErrors: any = {
    requiredPassword: false,
    dismatchPassword: false,
  };
  reason: string = '';

  @Action('login', { namespace }) login: any;
  @Action('fetchMyInfo', { namespace }) fetchMyInfo: any;

  get steemLoginUrl(): string {
    return Login.getSocialLoginUrl('steemconnect');
  }

  static getSocialLoginUrl(provider: string): string {
    return `${socialLoginBaseUrl}${provider}/`;
  }
  submit() {
    if (!this.username && !this.password) {
      this.$router.replace({ name: 'SignUp' });
      return;
    }
    if (!this.password) {
      this.formErrors.requiredPassword = true;
      this.formErrors.dismatchPassword = false;
      return;
    }

    this.formErrors.requiredPassword = false;
    this.formErrors.dismatchPassword = false;
    this.login({ username: this.username, password: this.password })
      .then((res: any) => { this.fetchMyInfo(); })
      .then(() => {
        this.$router.replace({ name: 'Home' });
      })
      .catch(() => {
        this.formErrors.requiredPassword = false;
        this.formErrors.dismatchPassword = true;
      });
  }
  showModal(text: string) {
    this.$modal.show('dialog', {
      title: '알림',
      text,
      buttons: [
        {
          title: '닫기',
        },
      ],
    });
  }
  mounted() {
    switch (this.$route.query.status) {
      case 'expired-session':
        this.showModal('세션이 만료되었습니다.<br>다시 로그인 하세요.');
        break;
      case 'inactive-user':
        this.showModal('비활성화 계정엔 로그인하지 못합니다.<br>고객센터에 문의 바랍니다.');
        break;
      case 'error':
        this.showModal('소셜 로그인 장애로 로그인을 실패하였습니다.<br>고객센터에 문의 바랍니다.');
        break;
    }
  }
}

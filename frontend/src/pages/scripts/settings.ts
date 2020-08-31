import _ from 'lodash';
import { AxiosError, AxiosResponse } from 'axios';
import Vue from 'vue';
import { Action, Getter, Mutation } from 'vuex-class';
import Component from 'vue-class-component';
import Cropper from 'cropperjs';
import ProfileImageComponent from '@/components/ProfileImage.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import * as T from '../../store/auth/types';
import { socialLoginBaseUrl } from '../../api';

require('cropperjs/src/css/cropper.css');

const namespace = 'auth';

enum EnumSections {
  SETTINGS,
  EDIT_PROFILE_IMAGE,
}

@Component({
  name: 'settings',
  components: {
    ProfileImageComponent,
    LoadingSpinner,
  },
})
export default class Settings extends Vue {
  isProfileLoaded: boolean = false;
  isSteemConnectLoaded: boolean = false;
  isAvailableSteemConnect: boolean = false;
  isEditing = {
    nickname: false,
  };
  newNickname = '';
  formErrors = {
    nickname: '',
  };
  editImage: string = '';
  editImageFilename: string = '';
  currentSection: EnumSections = EnumSections.SETTINGS;
  cropper!: Cropper;
  notificationSettings: T.IUserNotificationSettings = {
    liked_my_post: false,
    my_new_follower: false,
    following_new_post: false,
    new_comment_user_posted: false,
  };

  @Action('fetchMyInfo', { namespace }) fetchMyInfo: any;
  @Action('patchUserinfo', { namespace }) patchUserinfo: any;
  @Action('fetchSteemConnectAccountInfo', { namespace }) fetchSteemConnectAccountInfo: any;
  @Action('postProfileImage', { namespace }) postProfileImage: any;
  @Action('patchNotificationSettings', { namespace }) patchNotificationSettings: any;
  
  @Getter('username', { namespace }) username!: string | undefined;
  @Getter('userinfo', { namespace }) userinfo!: T.User;
  @Getter('getProfile', { namespace }) getProfile!: Function;

  @Mutation('logout', { namespace: 'auth' }) logoutMutation: any;

  get isEditProfileImageSection(): boolean {
    return this.currentSection === EnumSections.EDIT_PROFILE_IMAGE;
  }
  get nickname(): string | undefined  {
    return this.userinfo ? (this.userinfo as T.User).nickname : undefined;
  }

  get profile(): T.Profile | undefined {
    return this.getProfile(this.userinfo.username);
  }

  get steemLoginUrl(): string {
    return Settings.getSocialLoginUrl('steemconnect');
  }

  get steemUsername(): string | undefined {
    if (!this.userinfo) { return; }
  }

  static getSocialLoginUrl(provider: string): string {
    return `${socialLoginBaseUrl}${provider}/`;
  }

  async submitProfileImage() {
    const formdata = new FormData();
    formdata.append('filename', this.editImageFilename);
    formdata.append('content', this.cropper.getCroppedCanvas().toDataURL());
    try {
      await this.postProfileImage(formdata);
      await this.fetchMyInfo().catch(() => {});
      this.cancelEditProfileImage();
    } catch (e) {
      const res = (e as AxiosError).response as AxiosResponse;
      this.showModal(
        res.data.detail,
      );
      throw e;
    }
  }

  initCropper() {
    const imageElement = this.$refs.profileImageSrc as HTMLImageElement;
    imageElement.style.height = `${imageElement.width}px`;
    this.cropper = new Cropper(imageElement, {
      viewMode: 2,
      // dragMode: Cropper.DragMode.Move,
      dragMode: 'move' as any,
      aspectRatio: 1,
      cropBoxMovable: false,
      cropBoxResizable: false,
      autoCropArea: 0.8,
    });
  }

  openEditProfileImage() {
    if (!this.cropper) { this.initCropper(); }

    const el = (this.$refs.profileImageInput as any);
    if (!el.files || el.files.length === 0) { return; }
    const reader = new FileReader();

    reader.onload = (event: FileReaderProgressEvent) => {
      if (!event.target) { return; }
      this.editImage = event.target.result;
      this.cropper.replace(event.target.result);
      this.currentSection = EnumSections.EDIT_PROFILE_IMAGE;
    };

    reader.readAsDataURL(el.files[0]);
    this.editImageFilename = el.files[0].name;
  }

  cancelEditProfileImage() {
    this.editImage = '';
    this.cropper.clear();
    this.currentSection = EnumSections.SETTINGS;
  }

  openChangeNickname() {
    this.isEditing.nickname = true;
    this.$nextTick(() => {
      (this.$refs.inputNickname as HTMLInputElement).focus();
    });
  }
  cancelChangeNickname() {
    this.isEditing.nickname = false;
    this.newNickname = this.nickname || '';
  }

  async changeNickname() {
    if (!this.newNickname) {
      this.cancelChangeNickname();
      return;
    }
    try {
      await this.patchUserinfo({
        uid: (this.userinfo as T.IUser).uid,
        payload: { nickname: this.newNickname },
      });
      await this.fetchMyInfo().catch(() => {});
      this.cancelChangeNickname();
    } catch (e) {
      this.formErrors.nickname = _.isArray(e.response.data.nickname) ?
        e.response.data.nickname[0] :
        e.response.data.nickname;
    }
  }

  async checkSteemConnectToken() {
    if (!this.userinfo.social_auth) { return; }
    if (!_.has(this.userinfo.social_auth, 'steemconnect')) { return; }
    const token = _.get(_.get(this.userinfo.social_auth, 'steemconnect'), 'access_token');
    if (!token) { return; }

    this.isSteemConnectLoaded = false;
    try {
      await this.fetchSteemConnectAccountInfo(token);
      this.isSteemConnectLoaded = this.isAvailableSteemConnect = true;
    } catch (e) {
      this.isSteemConnectLoaded = true;
      this.isAvailableSteemConnect = false;
    }
  }

  logout() {
    this.logoutMutation();
    this.$router.replace({ name: 'Login' });
  }

  applyFetchedNotificationSettings() {
    if (!this.userinfo) { return; }
    this.notificationSettings = this.userinfo.notification_settings;
  }

  async updateNotificationSettings() {
    await this.patchNotificationSettings(this.notificationSettings);
  }

  async created() {
    if (!this.username) {
      this.logout();
      return;
    }
    this.isProfileLoaded = false;
    await this.fetchMyInfo().catch(() => {});
    this.applyFetchedNotificationSettings();
    this.isProfileLoaded = true;

    await this.checkSteemConnectToken();
  }

  showModal(text: string, closeHandler?: Function) {
    this.$modal.show('dialog', {
      title: '알림',
      text,
      buttons: [
        {
          title: '닫기',
          handler: (i: number, $event: any, params: any) => {
            if (_.isFunction(closeHandler)) {
              closeHandler();
            }
            this.$modal.hide('dialog');
          },
        },
      ],
    });
  }

  beforeMount() {
    if (this.cropper) { this.cropper.destroy(); }
  }

  copyCode (this: any) {
    const el = (this.$refs as any).permalink as HTMLInputElement;

    if (this.isiOS) {
      const oldContentEditable = el.contentEditable;
      const oldReadOnly = el.readOnly;
      const range = document.createRange();

      el.contentEditable = 'true';
      el.readOnly = true;
      range.selectNodeContents(el);

      const s = window.getSelection();
      s.removeAllRanges();
      s.addRange(range);

      el.setSelectionRange(0, 999999);

      el.contentEditable = oldContentEditable;
      el.readOnly = oldReadOnly;
    } else {
      el.setAttribute('type', 'text');
      el.select();
    }
    document.execCommand('copy');
    alert('추천코드가 복사되었습니다.');
  }
}

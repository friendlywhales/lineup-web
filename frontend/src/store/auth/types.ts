import 'reflect-metadata';
import _ from 'lodash';

export interface IPasswordForm {
  username: string;
  password: string;
}

export enum EnumUserLevel {
  ANONYMOUS = 'anonymous',
  ASSOCIATE = 'associate',
  CORPORATE = 'corporate',
  REGULAR = 'regular',
  AUTHOR = 'author',
}

export enum EnumOpenStatuses {
  PUBLIC = 'public',
  PRIVATE = 'private',
}

export interface IUserLineUpPointInfo {
  posting: number;
  comment: number;
  follow: number;
  login: number;
  signup: number;
  like: number;
  total: number;
}

export interface IUserNotificationSettings {
  liked_my_post: boolean;
  my_new_follower: boolean;
  following_new_post: boolean;
  new_comment_user_posted: boolean;
}

export interface IUser {
  username: string;
  email: string;
  image?: string;
  is_verified: boolean;
  level: EnumUserLevel;
  uid: string;
  has_promotion_codes?: string;
  signup_route?: string;
  nickname?: string;
  open_status?: string;
  social_auth?: {
    [provider: string]: ISocialAuthInfo,
  };
  lineup_points?: IUserLineUpPointInfo;
  has_daily_attendance?: null | boolean;  // tslint:disable-line:variable-name
  notification_settings: IUserNotificationSettings;
  recommended_code: string;  // tslint:disable-line:variable-name
}

export class User implements IUser {
  username: string;
  email: string;
  image?: string;
  is_verified: boolean;  // tslint:disable-line:variable-name
  level: EnumUserLevel;
  uid: string;
  has_promotion_codes?: string;  // tslint:disable-line:variable-name
  signup_route?: string;  // tslint:disable-line:variable-name
  open_status?: string;  // tslint:disable-line:variable-name
  social_auth?: {};  // tslint:disable-line:variable-name
  nickname?: string;
  lineup_points?: IUserLineUpPointInfo;  // tslint:disable-line:variable-name
  has_daily_attendance?: null | boolean;  // tslint:disable-line:variable-name
  notification_settings: IUserNotificationSettings;  // tslint:disable-line:variable-name
  recommended_code: string;  // tslint:disable-line:variable-name

  constructor(value: IUser) {
    this.username = value.username;
    this.nickname = value.nickname;
    this.email = value.email;
    this.image = value.image;
    this.is_verified = value.is_verified;
    this.level = EnumUserLevel[value.level.toString().toUpperCase() as keyof typeof EnumUserLevel];
    this.uid = value.uid;
    this.has_promotion_codes = value.has_promotion_codes;
    this.signup_route = value.signup_route;
    this.open_status = value.open_status;
    if (_.isObject(value.social_auth)) {
      this.social_auth = {};
      _.forEach(value.social_auth, (v: ISocialAuthInfo, k: string) => {
        (this.social_auth as any)[k] = new SocialAuthInfo(v);
      });
    }
    this.lineup_points = value.lineup_points;
    this.has_daily_attendance = value.has_daily_attendance;
    this.notification_settings = value.notification_settings;
    this.recommended_code = value.recommended_code;
  }

  isLoggedIn(): boolean {
    return true;
  }
}

export interface ISocialAuthInfo {
  uid: string;
  username: string;
  expires: Date;
  access_token: string;
}

export class SocialAuthInfo implements ISocialAuthInfo {
  uid: string;
  username: string;
  expires: Date;
  access_token: string;  // tslint:disable-line:variable-name

  constructor(value: ISocialAuthInfo) {
    this.uid = value.uid;
    this.username = value.username;
    this.expires = new Date(value.expires);
    this.access_token = value.access_token;
  }
}

export class AnonymouseUser implements IUser {
  username: string = '';
  email: string = '';
  is_verified: boolean = false;  // tslint:disable-line:variable-name
  level: EnumUserLevel = EnumUserLevel.ANONYMOUS;
  uid: string = '';
  has_daily_attendance: null | boolean = null;  // tslint:disable-line:variable-name
  recommended_code: string = '';  // tslint:disable-line:variable-name
  notification_settings: IUserNotificationSettings = {  // tslint:disable-line:variable-name
    liked_my_post: false,
    my_new_follower: false,
    following_new_post: false,
    new_comment_user_posted: false,
  };

  isLoggedIn(): boolean {
    return false;
  }
}

export const anonymous = new AnonymouseUser();

export interface IProfile {
  uid: string;
  fullname?: string;
  username: string;
  nickname?: string;
  image?: string;
  level: EnumUserLevel;
  open_status: EnumOpenStatuses;
  is_verified: boolean;
  post_count: number;
  following_count: number;
  follower_count: number;
}

export class Profile implements IProfile {
  uid: string;
  fullname?: string;
  username: string;
  nickname?: string;
  image?: string;
  level: EnumUserLevel;
  open_status: EnumOpenStatuses;  // tslint:disable-line:variable-name
  is_verified: boolean;  // tslint:disable-line:variable-name
  post_count: number;  // tslint:disable-line:variable-name
  following_count: number;  // tslint:disable-line:variable-name
  follower_count: number;  // tslint:disable-line:variable-name

  constructor(value: IProfile) {
    this.uid = value.uid;
    this.fullname = value.fullname;
    this.username = value.username;
    this.nickname = value.nickname;
    this.image = value.image;
    this.level = EnumUserLevel[value.level.toString().toUpperCase() as keyof typeof EnumUserLevel];
    this.open_status = EnumOpenStatuses[
      value.open_status.toString().toUpperCase() as keyof typeof EnumOpenStatuses
    ];
    this.is_verified = value.is_verified;
    this.post_count = value.post_count;
    this.following_count = value.following_count;
    this.follower_count = value.follower_count;
  }
}

export interface SignUpForm  {
  email: string;
  password: string;
}

export interface PromotionCode {
  value: string;
  extra?: any;
  is_active: boolean;
  is_available: boolean;
  expired_at: Date | null;
}

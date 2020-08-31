
import * as T from './types';

export interface IAuthState {
  info: T.IUser;
  profiles: {
    [username: string]: T.IProfile,
  };
  followings: {
    [username: string]: boolean,
  };
  followers: {
    [username: string]: boolean,
  };
}

const state: IAuthState = {
  info: T.anonymous,
  followings: {},
  followers: {},
  profiles: {},
};

export default state;

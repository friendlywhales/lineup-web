
import * as T from './types';

export interface IMessagingState {
  notifications: {
    following: T.INotification[],
    reward: T.INotification[],
  };
}

const state: IMessagingState = {
  notifications: {
    following: [],
    reward: [],
  },
};

export default state;

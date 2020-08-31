
import * as T from './types';

export interface IContentsState {
  posts: {
    [username: string]: {
      items: T.Post[],
      total: number,
      next?: string,
      previous?: string,
    },
  };
  postUidsUsername: {
    [username: string]: string,
  };
  isVisibleUploadPage: boolean;
  draftPost?: T.IDraftPost;
  collections: {
    [username: string]: T.ICollection[],
  };
  collectionUidsUsername: {
    [username: string]: string,
  };
  collectionPosts: {
    [uid: string]: T.IPost[],
  };
  inputSearchTerm: string;
  collectionsPerPost: {
    [uid: string]: string[],
  };
  timeline: {
    posts: T.Post[],
  };
}

const state: IContentsState = {
  posts: {},
  postUidsUsername: {},
  isVisibleUploadPage: false,
  draftPost: undefined,
  collections: {},
  collectionPosts: {},
  collectionUidsUsername: {},
  inputSearchTerm: '',
  collectionsPerPost: {},
  timeline: {
    posts: [],
  },
};

export default state;

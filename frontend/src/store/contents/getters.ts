
import { Module, GetterTree } from 'vuex';
import _ from 'lodash';
import { IContentsState } from './state';
import * as T from './types';
import * as rT from '../types';

export function getProfilePosts(state: IContentsState): Function {
  return (username: string) => state.posts[username];
}

export function getPostByUid(state: IContentsState): Function {
  return (uid: string) => {
    const username = _.get(state.postUidsUsername, uid);
    const hasPosts = _.has(state.posts, username);
    return username && hasPosts
      ? _.find(state.posts[username].items, { uid })
      : undefined;
  };
}

export function getComments(state: IContentsState): Function {
  return (uid: string) => {
    const post = getPostByUid(state)(uid);
    return post ? post.comments : [];
  };
}

export function isVisibleUploadPage(state: IContentsState): boolean {
  return state.isVisibleUploadPage;
}

export function draftPost(state: IContentsState): T.IDraftPost | undefined {
  return state.draftPost;
}

export function getUserCollections(state: IContentsState): Function {
  return (username: string) => state.collections[username] || [];
}

export function getCollection(state: IContentsState): Function {
  return (uid: string) => {
    const username = _.get(state.collectionUidsUsername, uid);
    if (!username) return undefined;
    return _.find(state.collections[username] || [], { uid });
  };
}

export function getCollectionPosts(state: IContentsState): Function {
  return (uid: string) => state.collectionPosts[uid] || [];
}

export function currentInputSearchTerm(state: IContentsState): string {
  return state.inputSearchTerm;
}

export function collectionsPerPost(state: IContentsState): any {
  return state.collectionsPerPost;
}

export function hasCollectionPost(state: IContentsState): Function {
  return (postUid: string, collectionUid: string): boolean => {
    if (!_.has(state.collectionsPerPost, postUid)) {
      state.collectionsPerPost[postUid] = [];
      return false;
    }
    return _.indexOf(state.collectionsPerPost[postUid], collectionUid) > -1;
  };
}

export function getCollectionUidOfPost(state: IContentsState): Function {
  return (postUid: string): string[] => {
    return _.get(state.collectionsPerPost, postUid, []);
  };
}

export function timelinePosts(state: IContentsState): T.Post[] {
  return state.timeline.posts;
}

export default <GetterTree<IContentsState, rT.IRootState>> {
  getProfilePosts,
  getPostByUid,
  getComments,
  isVisibleUploadPage,
  draftPost,
  getUserCollections,
  getCollectionPosts,
  getCollection,
  currentInputSearchTerm,
  hasCollectionPost,
  timelinePosts,
  getCollectionUidOfPost,
  collectionsPerPost,
};

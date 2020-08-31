
import Vue from 'vue';
import { MutationTree } from 'vuex';
import _ from 'lodash';
import * as T from './types';
import { IContentsState } from './state';

export function appendProfilePosts(
  state: IContentsState,
  params: { username: string; posts: T.IPost[]; reverse?: boolean },
) {
  if (!params.username) return;
  if (!_.has(state.posts, params.username)) resetProfilePosts(state, params.username);

  _.forEach(params.posts, (item) => {
    if (_.findIndex(state.posts[params.username].items, { uid: item.uid }) > -1) {
      return;
    }
    state.postUidsUsername[item.uid] = params.username;
    state.posts[params.username].items = _.union(...(params.reverse === true
      ? [[item], state.posts[params.username].items]
      : [state.posts[params.username].items, [item]]));
  });
}

export function resetProfilePosts(state: IContentsState, username: string) {
  if (!username) return;
  const defaultValue = {
    items: [],
    total: 0,
    next: undefined,
    previous: undefined,
  };
  Vue.set(state.posts, username, defaultValue);
}

export function updateProfileTotalPostNumber(state: IContentsState,
                                             params: { username: string, total: string | number }) {
  state.posts[params.username].total = _.isInteger(params.total)
    ? params.total as number
    : _.toInteger(params.total);
}

export function updateCursorPaginationOffsets(
  state: IContentsState,
  params: {
    username: string, next?: string, previous?: string,
  }) {
  state.posts[params.username].next = params.next;
  state.posts[params.username].previous = params.previous;
}

export function updatePost(state: IContentsState, item: T.Post) {
  if (!_.has(state.posts, item.user)) resetProfilePosts(state, item.user);

  const index = _.findIndex(state.posts[item.user].items, { uid: item.uid });
  if (index === -1) {
    state.posts[item.user].items.push(item);
  } else {
    state.posts[item.user].items[index] = item;
  }
  state.postUidsUsername[item.uid] = item.user;
}

export function deleteUserPost(state: IContentsState, params: { uid: string, username: string }) {
  const posts = _.get(state.posts, params.username);
  if (!posts) { return; }
  const index = _.findIndex(posts.items, { uid: params.uid });
  if (index === -1) { return; }
  _.remove(state.posts[params.username].items, o => o.uid === params.uid);
}

export function toggleLike(state: IContentsState,
                           params: { uid: string, user: string, hasLiked: boolean }) {
  const username = _.get(state.postUidsUsername, params.uid);
  if (!username) return;

  const post = _.find(state.posts[username].items, { uid: params.uid });
  if (!post) return;

  const exists = post.likes.indexOf(params.user);
  if (params.hasLiked && exists === -1) {
    post.likes.push(params.user);
    return;
  }
  if (!params.hasLiked && exists !== -1) {
    _.pull(post.likes, params.user);
  }
}

export function appendComment(state: IContentsState,
                              params: { uid: string, user: string, comment: T.IComment }) {
  const username = _.get(state.postUidsUsername, params.uid);
  if (!username) return;

  const post = _.find(state.posts[username].items, { uid: params.uid });
  if (!post) return;

  if (!post.comments) post.comments = [];
  post.comments.push(new T.Comment(params.comment));
}

export function toggleUploadPage(state: IContentsState, status: boolean) {
  state.isVisibleUploadPage = status;
}

export function applyDraftPost(state: IContentsState, post: T.IDraftPost) {
  state.draftPost = post;
}

export function appendAttachmentToDraftPost(state: IContentsState, item: T.IAttachment) {
  if (!state.draftPost) return;
  state.draftPost.attachments.push(item);
}

export function removeDraftPost(state: IContentsState) {
  state.draftPost = undefined;
}

export function updateUserCollection(state: IContentsState, item: T.ICollection) {
  if (!_.has(state.collections, item.user)) {
    Vue.set(state.collections, item.user, []);
  }
  const index = _.findIndex(state.collections[item.user], { uid: item.uid });
  if (index > -1) {
    state.collections[item.user][index] = item;
  } else {
    state.collections[item.user].push(item);
  }
  state.collectionUidsUsername[item.uid] = item.user;
}

export function updateCollectionPosts(state: IContentsState,
                                      params: { uid: string, items: T.IPost[] }) {
  if (!_.has(state.collectionPosts, params.uid)) {
    Vue.set(state.collectionPosts, params.uid, []);
  }
  _.forEach(params.items, (item) => {
    updateCollectionsPerPost(state, { postUid: item.uid, collectionUid: params.uid });

    if (_.findIndex(state.collectionPosts[params.uid], { uid: item.uid }) > -1) {
      return;
    }
    state.collectionPosts[params.uid].push(item);
  });
}

export function inputSearchTerm(state: IContentsState, term: string) {
  state.inputSearchTerm = term;
}

export function updateCollectionsPerPost(state: IContentsState,
                                         params: { postUid: string, collectionUid: string }) {
  if (!_.has(state.collectionsPerPost, params.postUid)) {
    Vue.set(state.collectionsPerPost, params.postUid, []);
  }
  if (_.indexOf(state.collectionsPerPost[params.postUid], params.collectionUid) > -1) {
    return;
  }
  state.collectionsPerPost[params.postUid].push(params.collectionUid);
}

export function detachPostToCollections(state: IContentsState,
                                        params: { postUid: string, collectionUid: string }) {
  if (!_.has(state.collectionsPerPost, params.postUid)) {
    Vue.set(state.collectionsPerPost, params.postUid, []);
    return;
  }
  const index = _.indexOf(state.collectionsPerPost[params.postUid], params.collectionUid);
  if (index === -1) { return; }
  state.collectionsPerPost[params.postUid].splice(index, 1);
}

export function updateTimelinePosts(state: IContentsState,
                                    params: { post: T.Post }) {
  const index = _.findIndex(state.timeline.posts, { uid: params.post.uid });
  if (index === -1) {
    state.timeline.posts.push(params.post);
  } else {
    state.timeline.posts[index] = params.post;
  }
}

export function deleteTimelinePost(state: IContentsState, uid: string) {
  _.remove(state.timeline.posts, o => o.uid === uid);
}

export default <MutationTree<IContentsState>> {
  appendProfilePosts,
  resetProfilePosts,
  updateProfileTotalPostNumber,
  updateCursorPaginationOffsets,
  updatePost,
  deleteUserPost,
  toggleLike,
  appendComment,
  toggleUploadPage,
  applyDraftPost,
  appendAttachmentToDraftPost,
  removeDraftPost,
  updateUserCollection,
  updateCollectionPosts,
  inputSearchTerm,
  updateCollectionsPerPost,
  detachPostToCollections,
  updateTimelinePosts,
  deleteTimelinePost,
};

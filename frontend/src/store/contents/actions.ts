
import _ from 'lodash';
import { ActionTree, ActionContext, Store } from 'vuex';
import axios, { AxiosResponse } from 'axios';
import { IContentsState } from './state';
import * as T from './types';
import { EnumHttpStatus } from '../types';
import api, { customHeaders } from '../../api';

export default <ActionTree<IContentsState, any>> {
  async fetchProfilePosts({ commit },
                          params: { username: string, next?: string }): Promise<EnumHttpStatus> {
    const url = `/accounts/profiles/${params.username}/posts/?uid=${params.next || ''}`;
    const res: AxiosResponse = await api.get(url);
    commit('resetProfilePosts');
    commit('appendProfilePosts', { username: params.username, posts: res.data.results });
    commit('updateProfileTotalPostNumber', {
      username: params.username,
      total: _.get(res.headers, customHeaders.entityTotalNumber, 0),
    });
    commit('updateCursorPaginationOffsets', {
      username: params.username,
      next: res.data.next,
      previous: res.data.previous,
    });
    return EnumHttpStatus.OK;
  },

  async fetchPosts({ commit }, url?: string): Promise<T.IPaginatedTimeline> {
    return api
      .get(url || '/contents/posts/')
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchSearchAllPosts({ commit }, url?: string): Promise<T.IPaginatedTimeline> {
    return api
      .get(url || '/contents/posts/search-all/')
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchPost({ commit }, uid: string): Promise<T.Post> {
    const res: AxiosResponse = await api.get(`/contents/posts/${uid}/`);
    const post = new T.Post(res.data);
    commit('updatePost', post);
    return post;
  },

  async toggleLike({ commit, rootGetters }, uid: string): Promise<void> {
    return api
      .post(`/contents/posts/${uid}/likes/`)
      .then((res: any) => {
        commit('toggleLike', {
          uid,
          user: rootGetters['auth/userinfo'].username,
          hasLiked: res.status !== 204,
        });
      });
  },

  async postComment({ commit, rootGetters },
                    params: { uid: string, content: string }): Promise<void> {
    return api
      .post(`/contents/posts/${params.uid}/comments/`, { content: params.content })
      .then((res: any) => {
        commit('appendComment', {
          uid: params.uid,
          user: rootGetters['auth/userinfo'].username,
          comment: res.data,
        });
      });
  },

  async createDraftPost({ commit }): Promise<T.IPost> {
    return api.post('/contents/posts/').then((res: any) => {
      commit('applyDraftPost', {
        uid: res.data.uid,
        content: '',
        attachments: [],
      });
      return res.data;
    });
  },

  async uploadPostAttachment(
    { commit },
    params: { uid: string, formdata: FormData },
  ): Promise<T.IAttachment[]> {
    return api
      .post(`/contents/posts/${params.uid}/attachments/`, params.formdata)
      .then((res: any) => {
        _.forEach(res.data, (o) => {
          commit('appendAttachmentToDraftPost', o);
        });
        return res.data;
      });
  },

  async patchPost({ commit }, params: { uid: string, data: T.IEditPost }): Promise<T.Post> {
    return api
      .patch(`/contents/posts/${params.uid}/`, params.data)
      .then((res: any) => res.data);
  },

  async publishPost({ commit }, uid: string): Promise<T.Post> {
    return api
      .post(`/contents/posts/${uid}/publish/`)
      .then((res: any) => res.data);
  },

  async fetchUserCollections({ commit }, username?: string): Promise<T.ICollection[]> {
    return api
      .get(`/accounts/${username ? 'profiles/' + username : 'users'}/collections/`)
      .then((res: any) => {
        _.forEach(res.data, (item: T.ICollection) => {
          commit('updateUserCollection', item);
        });
        return res.data;
      });
  },

  async fetchCollectionPosts({ commit }, uid: string): Promise<void> {
    return api
      .get(`/contents/collections/${uid}/posts/`)
      .then((res: any) => {
        commit('updateCollectionPosts', { uid, items: res.data.results });
      });
  },

  async fetchTags({ commit }, term: string): Promise<T.ITag[]> {
    return api
      .get(`/contents/tags/${term}/`)
      .then((res: any) => {
        return res.data;
      });
  },

  async fetchTagPosts({ commit }, term: string): Promise<T.IPost[]> {
    return api
      .get(`/contents/tags/${term}/posts/`)
      .then((res: any) => {
        return res.data.results;
      });
  },

  async createCollection({ commit }, name: string): Promise<void> {
    return api
      .post('/contents/collections/', { name })
      .then((res: any) => {
        commit('updateUserCollection', res.data);
        return res.data;
      });
  },

  async addPostToCollection({ commit },
                            params: { post: T.Post, collection: T.ICollection }): Promise<void> {
    return api
      .post(
        `/contents/collections/${params.collection.uid}/posts/`,
        { post: params.post.uid },
        )
      .then((res: any) => {
        _.forEach(res.data.results, (item: any) => {
          commit(
            'updateCollectionsPerPost',
            { postUid: item.uid, collectionUid: params.collection.uid },
          );
        });
        //
        return res.data;
      });
  },

  async removePostToCollection(
    { commit }, params: { post: T.Post, collection: T.ICollection },
  ): Promise<boolean> {
    return api
      .post(
        `/contents/collections/${params.collection.uid}/detach-post/`,
        { post: params.post.uid },
      )
      .then((res: any) => {
        commit(
          'detachPostToCollections',
          { postUid: params.post.uid, collectionUid: params.collection.uid },
        );
        return res.status === 200;
      });
  },

  async hasCollectedPost({ commit }, uid: string): Promise<boolean> {
    return api
      .get(`/contents/posts/${uid}/has-collected/`)
      .then((res: any) => {
        _.forEach(res.data, (item: T.ICollection) => {
          commit('updateCollectionsPerPost', { postUid: uid, collectionUid: item.uid });
        });
        return res.status === 200;
      });
  },

  async fetchTimeline({ commit }, url?: string): Promise<T.IPaginatedTimeline> {
    return api
      .get(url || '/contents/posts/timeline/')
      .then((res: any) => {
        _.forEach(res.data.results, (item: T.IPost) => {
          commit('updateTimelinePosts', { post: new T.Post(item) });
        });
        return res.data;
      });
  },

  async reportPost({ commit }, params: { uid: string, payload: any }): Promise<boolean> {
    return api
      .post(
        `/contents/posts/${params.uid}/report/`,
        params.payload,
      )
      .then((res: any) => {
        return true;
      });
  },

  async deletePost({ commit }, params: { uid: string, username: string }): Promise<string> {
    return api
      .delete(`/contents/posts/${params.uid}/`)
      .then((res: any) => {
        commit('deleteUserPost', params);
        commit('deleteTimelinePost', params.uid);
        return params.uid;
      });
  },
};

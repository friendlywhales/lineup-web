import 'reflect-metadata';

export interface IPost {
  uid: string;
  user: string;
  nickname?: string;
  user_image?: string;
  images: string[];
  thumbnails: IThumbnail[];
  content?: string;
  tags: ITag[];
  updated_at: Date;
  likes: string[];
  comments?: IComment[];
  orig_content?: string;
  restrict_code: string | null;
}

export class Post implements IPost {
  uid: string;
  user: string;
  nickname?: string;
  user_image?: string;  // tslint:disable-line:variable-name
  images: string[];
  thumbnails: IThumbnail[];
  content?: string;
  tags: ITag[];
  updated_at: Date;  // tslint:disable-line:variable-name
  likes: string[];
  comments?: Comment[];
  orig_content?: string;  // tslint:disable-line:variable-name
  restrict_code: string | null;  // tslint:disable-line:variable-name

  constructor(value: IPost) {
    this.uid = value.uid;
    this.user = value.user;
    this.nickname = value.nickname;
    this.user_image = value.user_image;
    this.images = value.images;
    this.thumbnails = value.thumbnails;
    this.content = value.content;
    this.tags = value.tags;
    this.likes = value.likes;
    this.comments = value.comments;
    this.updated_at = new Date(value.updated_at.toString());  // tslint:disable-line:variable-name
    if (value.orig_content) {
      this.orig_content = value.orig_content;
    }
    this.restrict_code = value.restrict_code;
  }
}

export interface IThumbnail {
  url: string;
  width: number;
  height: number;
}

export interface ITag {
  name: string;
  post_number?: number;
}

export interface IComment {
  uid: string;
  post: string;
  user: string;
  nickname?: string;
  content: string;
  reply?: string;
  created_at: Date;
}

export class Comment implements IComment {
  uid: string;
  post: string;
  user: string;
  nickname?: string;
  content: string;
  reply?: string;
  created_at: Date;  // tslint:disable-line:variable-name

  constructor(value: IComment) {
    this.uid = value.uid;
    this.post = value.post;
    this.user = value.user;
    this.nickname = value.nickname;
    this.content = value.content;
    this.reply = value.reply;
    this.created_at = new Date(value.created_at);  // tslint:disable-line:variable-name
  }
}

export interface IEditPost {
  content: string;
}

export interface IDraftPost {
  uid: string;
  content: string;
  attachments: IAttachment[];
}

export interface IAttachment {
  post: string;
  content: string;
  order: number;
  kind: string;
}

export interface ICollection {
  uid: string;
  user: string;
  name: string;
  title_images: string[];
}

export interface IPaginatedTimeline {
  next: string | null;
  previous: string | null;
  results: IPost[];
}

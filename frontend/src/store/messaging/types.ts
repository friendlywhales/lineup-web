import 'reflect-metadata';

import * as cT from '@/store/contents/types';

export interface INotification {
  uid: string;
  trigger: string;
  kind: string;
  extra: any;
  content: any;
  created_at: Date;
  hasRead?: boolean;
  thumbnails: cT.IThumbnail[];
}

export class Notification implements INotification {
  uid: string;
  trigger: string;
  kind: string;
  extra: any;
  content: any;
  created_at: Date;  // tslint:disable-line:variable-name
  hasRead?: boolean;
  thumbnails: cT.IThumbnail[];

  constructor(value: INotification) {
    this.uid = value.uid;
    this.trigger = value.trigger;
    this.kind = value.kind;
    this.extra = value.extra;
    this.content = value.content;
    this.created_at = new Date(value.created_at);  // tslint:disable-line:variable-name
    this.hasRead = value.hasRead || false;
    this.thumbnails = value.thumbnails;
  }
}

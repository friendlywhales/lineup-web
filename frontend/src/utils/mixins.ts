
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { format as datetimeFormat } from 'date-fns';
import distanceInWordsToNow from 'date-fns/distance_in_words_to_now';
// var eoLocale = require('date-fns/locale/eo')
import koLocale from 'date-fns/locale/ko';

@Component
export class FormatMixin extends Vue {
  dateFormat(value: Date, dateFormat= 'YY.MM.DD'): string {
    return datetimeFormat(value, dateFormat);
  }
  timeFormat(value: Date, timeFormat= 'HH:mm'): string {
    return datetimeFormat(value, timeFormat);
  }
  distanceInWordsToNow(value: Date | string): string {
    return distanceInWordsToNow(_.isString(value) ? new Date(value) : value, { locale: koLocale });
  }
}

@Component
export class RouteMixin extends Vue {
  get pageName(): string {
    return this.$route.name || '';
  }
  isChildPageOf(name: string): boolean {
    return _.findIndex(this.$route.matched, { name }) > -1;
  }
}

@Component
export class UtilMixin extends Vue {
  get isiOS(): boolean {
    return !!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform);
  }
}

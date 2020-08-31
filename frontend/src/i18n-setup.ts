import Vue from 'vue';
import VueI18n from 'vue-i18n';
import axios from 'axios';
import client from './api';
import messages from './locale/messages';

Vue.use(VueI18n);

export const defaultLanguage = 'ko';

export const i18n = new VueI18n({
  locale: defaultLanguage,
  fallbackLocale: defaultLanguage,
  messages,
});

const loadedLanguages = ['ko', 'en'];

export function getCurrentLocale(): string {
  return localStorage.getItem('locale') || defaultLanguage;
}

export function setI18nLanguage(lang: string) {
  i18n.locale = lang;
  localStorage.setItem('locale', lang);
  axios.defaults.headers.common['Accept-Language'] = lang;
  client.client.defaults.headers.common['Accept-Language'] = lang;
  ((document as HTMLDocument).querySelector('html') as any).setAttribute('lang', lang);
  return lang;
}

export function loadLanguageAsync(lang: string) {
  if (i18n.locale !== lang) {
    if (!loadedLanguages.includes(lang)) {
      return import(/* webpackChunkName: "lang-[request]" */ `@/locale/messages/${lang}`) // tslint:disable-line:space-in-parens max-line-length
        .then((msgs: any) => {
          i18n.setLocaleMessage(lang, msgs.default);
          loadedLanguages.push(lang);
          return setI18nLanguage(lang);
        });
    }
    return Promise.resolve(setI18nLanguage(lang));
  }
  return Promise.resolve(lang);
}

<template>
  <div class="container-wrapper">
    <div class="icon-sad-face container">
      <h3 class="error__title">서비스 점검 중입니다.</h3>
      <div class="error__description">
        더 나은 서비스 제공을 위해 서버 확장 중입니다.<br>
        예상 완료 시각은 1시입니다.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from "vue";
import Component from "vue-class-component";

interface IErrorData {
  title: string;
  description?: string;
}
interface IError {
  [type: string]: IErrorData;
}

export const errors: IError = {
  'invalid-steem-extra-data': {
    title: '스팀 계정 인증 오류',
    description: '스팀 계정으로부터 부정확한 인증 정보가 전달되어 로그인에 실패했습니다.',
  },
  'page-not-found': {
    title: '요청하신 페이지를 찾을 수 없습니다.',
  },
  'failure-from-social-auth': {
    title: '소셜 계정 인증 오류',
    description: '소셜 계정 인증 중 인증 제공자로부터 인증이 거절되어 로그인에 실패했습니다.',
  },
};

const requiredLoginTypes = [
  'invalid-steem-extra-data',
];

@Component({ name: 'error-page' })
export default class ErrorPage extends Vue {
  errorType!: string;
  error!: IErrorData;

  get isRequiredLogin(): boolean {
    return requiredLoginTypes.indexOf(this.errorType) !== -1;
  }
  created() {
    this.errorType = this.$route.params.type as string;
    this.error = _.get(errors, this.errorType, errors['page-not-found']);
  }
}
</script>

<style lang="scss" scoped>
  @import '../assets/styles/base.scss';
  .container-wrapper {
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-sad-face {
    background-size: 72px 70px;
    background-position: center top;
  }
  .container {
    padding: 92px 0 calc(92px + 1.125rem);
    font-size: 1.125rem;
    color: #b3b3b3;
    font-weight: bold;
    width: 100%;
  }
  .error__description {
    padding: 20px;
    line-height: 1.55;
    word-break: keep-all;
    word-wrap: break-word;
  }
  .button {
    display: block;
    color: #fff;
    padding: 15px 0;
    width: 85%;
    margin: 0 auto;
    background-color: #9347a9;
    @include vendor-prefix(border-radius, 100px);
  }
</style>

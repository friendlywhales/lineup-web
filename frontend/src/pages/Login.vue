<template>
  <div class="login-container">
    <form method="POST" @submit.prevent="submit" class="login-form">
      <div class="login-form__control">
        <input type="text"
               v-model="username"
               placeholder="LineUp 계정명 또는 email"
               class="login-form__input login-form__input-username">
      </div>
      <div class="login-form__control">
        <input type="password"
               v-model="password"
               placeholder="비밀번호"
               class="login-form__input login-form__input-password">
      </div>
      <div class="login-form__control login-form__errors" v-if="formErrors.requiredPassword || formErrors.dismatchPassword">
        <i class="icon icon-warning"></i>
        <span v-if="formErrors.requiredPassword">비밀번호를 입력해주세요</span>
        <span v-if="formErrors.dismatchPassword">E-mail 주소나 비밀번호가 일치하지 않습니다</span>
      </div>
      <div class="login-form__control login-form__remember-me-control">
        <input type="checkbox" id="remember-me" v-model="rememberMe" class="login-form__checkbox login-form__input-remember-me">
        <label for="remember-me" class="login-form__label login-form__label-remember-me">Remember me</label>
      </div>
      <div class="login-form__control login-form__button-control">
        <button type="submit" class="login-form__login-button login-form__login-lineup">라인업 계정으로 로그인 또는 가입</button>
        <span class="login-form__split-line">OR</span>
        <a :href="steemLoginUrl" class="login-form__login-button login-form__login-steemit">스팀잇 계정으로 로그인 또는 가입</a>
      </div>
    </form>

    <v-dialog width="72.5%" height="auto"></v-dialog>

    <modals-container/>
  </div>
</template>

<script lang="ts">
import Login from './scripts/login';
export default Login;
</script>

<style lang="scss" scoped>
@import '~@/assets/styles/base.scss';
@import '~@/assets/styles/icons.scss';

.login-form__control {
  padding: 5px 0;
  width: 85%;
  margin: 0 auto;
  box-sizing: border-box;
  display: flex;
  align-items: center;

  &.login-form__button-control {
    display: block;
    margin-top: 15px;
  }
}

.login-form__input {
  @include vendor-prefix(border-radius, 4px);
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, .0975);
  padding: 10px 5px;
  width: 100%;
  box-sizing: border-box;
  @include vendor-prefix(border-radius, 0);

  @include placeholder {
    color: #888;
    font-size: 0.75rem;
  }
  &:focus {
    border: none;
    border-bottom: 1px solid #9347a9;
    outline: 0;
  }
}
.login-form__label {
  color: rgba(0, 0, 0, .575);
  font-size: 0.8rem;
}
.login-form__input-remember-me {
  display: none;

  &:checked + .login-form__label-remember-me {
    background: url("~@/assets/styles/images/checkbox--checked.svg") no-repeat left center;
    background-size: contain;
  }
}
.login-form__label-remember-me {
  background: url("~@/assets/styles/images/checkbox.svg") no-repeat left center;
  background-size: contain;
  padding-left: 20px;
  color: #888;
}

.login-form__login-button {
  display: block;
  border: none;
  padding: 15px 0;
  width: 85%;
  margin: 0 auto;
  font-weight: bold;
  flex-grow: 1;
  box-sizing: border-box;
  font-size: 0.875rem;
  @include vendor-prefix(border-radius, 25px);

  &.login-form__login-lineup {
    background-color: #9347a9;
    color: #fff;
  }
  &.login-form__login-steemit {
    color: #39d6a6;
    border: 1px solid #39d6a6;
  }

  .login-form__split-line {
    font-size: 0.8rem;
  }
}
.login-form__split-line {
  display: block;
  margin: 30px auto 16px;
  width: 85%;
  overflow: hidden;
  text-align: center;
  font-size: 0.75rem;
  font-weight: bold;
  color: #ddd;

  &:before,
  &:after {
    background-color: #ddd;
    content: "";
    display: inline-block;
    height: 1px;
    position: relative;
    vertical-align: middle;
    width: 50%;
  }
  &:before {
    right: 0.5em;
    margin-left: -50%;
  }
  &:after {
    left: 0.5em;
    margin-right: -50%;
  }
}
  .login-form__errors {
    color: #f03d44;
    font-size: 0.75rem;

    .icon-warning {
      margin-right: 2px;
    }
  }
</style>

<style lang="scss">
  .vue-dialog-button {
    text-align: right;
  }
</style>

<template>
  <div>
    <form class="form__signup" @submit.prevent="submit">
      <div class="form-control">
        <div class="wrapper">
          <label for="form-email" :class="['form__label', {'has-error': errors.first('email')}]">E-mail</label>
          <input type="email" id="form-email" class="form__input" required
                 v-validate="'required|email'" name="email" v-model="email">
        </div>
        <div class="form-errors" v-show="errors.first('email')">
          <i class="icon icon-warning"></i>
          {{ errors.first('email') }}
        </div>
      </div>
      <div class="form-control">
        <div class="wrapper">
          <label for="form-email-again" :class="['form__label', {'has-error': errors.first('emailConfirm')}]">Confirm E-mail</label>
          <input type="email" id="form-email-again" class="form__input" required
                 v-validate="'required|email|confirmed:email'"  name="emailConfirm" v-model="emailConfirm">
        </div>
        <div class="form-errors" v-show="errors.first('emailConfirm')">
          <i class="icon icon-warning"></i>
          {{ errors.first('emailConfirm') }}
        </div>
      </div>
      <div class="form-control">
        <div class="wrapper">
          <label for="form-password" :class="['form__label', {'has-error': errors.first('password1')}]">Password</label>
          <input type="password" id="form-password" class="form__input" required
                v-validate="'required|min:6'" name="password1" v-model="password1">
        </div>
        <div class="form-errors" v-show="errors.first('password1')">
          <i class="icon icon-warning"></i>
          {{ errors.first('password1') }}
        </div>
      </div>
      <div class="form-control">
        <div class="wrapper">
          <label for="form-password2" :class="['form__label', {'has-error': errors.first('password2')}]">Confirm Password</label>
          <input type="password" id="form-password2" class="form__input" required
                v-validate="'required|confirmed:password1'" name="password2" v-model="password2">
        </div>
        <div class="form-errors" v-show="errors.first('password2')">
          <i class="icon icon-warning"></i>
          {{ errors.first('password2') }}
        </div>
      </div>
      <!--<div class="form-control">-->
        <!--<div class="wrapper">-->
          <!--<label for="form-coupon" class="form__label">Coupon</label>-->
          <!--<input type="text" id="form-coupon" class="form__input" v-model="promotionCode">-->
        <!--</div>-->
      <!--</div>-->
      <div class="form-control">
        <div class="wrapper">
          <label for="form-coupon" class="form__label">Recommended Code</label>
          <input type="text" id="form-coupon"
                 :class="['form__input', {'recommended-code__valid': isValidRecommendedCode === true, 'recommended-code__invalid': isValidRecommendedCode === false}]"
                 @input.stop.prevent="checkRecommendedCode($event)"
                 v-model="recommendedCode">
        </div>
      </div>


      <div class="form-control form-control__buttons">
          <button type="button" @click="cancel" class="form__button button__cancel">취소</button>
          <button type="submit" class="form__button button__submit">회원가입</button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import * as T from '@/store/auth/types';

const namespace = 'auth';

const recommendedCodeLength = 8;

// todo: do refactoring ASAP!!!

@Component
export default class App extends Vue {
  email: string = '';
  emailConfirm: string = '';
  password1: string = '';
  password2: string = '';
  promotionCode: string = '';
  recommendedCode: string = '';
  isValidRecommendedCode: boolean | null = null;
  passPromotionCode: boolean = true;
  hasFinished: boolean = false;

  @Action('signup', { namespace }) signup: any;
  @Action('login', { namespace }) login: any;
  @Action('fetchPromotionCode', { namespace }) fetchPromotionCode: any;
  @Action('consumePromotionCode', { namespace }) consumePromotionCode: any;
  @Action('checkRecommendedCode', { namespace }) checkRecommendedCodeAction: any;

  cancel() {
    this.$router.replace({ name: 'TopPage' });
  }
  checkPromotionCode(): Promise<T.PromotionCode> {
    if (!this.promotionCode) {
      return new Promise((resolve, reject) => {
        return resolve();
      });
    }
    return this.fetchPromotionCode(this.promotionCode);
  }
  async doSignup() {
    if (this.hasFinished) { return; }
    if (!this.passPromotionCode) { return; }

    const payload = {
      email: this.email,
      password: this.password1,
      recommended_code: this.recommendedCode,
    };

    try {
      const user = await this.signup(payload);
      this.login({ username: user.username, password: this.password1 })
        .then((res: any) => {
          if (this.promotionCode && this.passPromotionCode) {
            this.consumePromotionCode(this.promotionCode).then((res: any) => {
              this.hasFinished = true;
              alert('회원가입을 완료했습니다.');
              this.$router.replace({ name: 'Home' });
            });
            return;
          }
          this.hasFinished = true;
          this.isValidRecommendedCode = true;
          alert('회원가입을 완료했습니다.');
          this.$router.replace({ name: 'Home' });
        });
    } catch (err) {
      if (err.response.data.code === 'invalid-recommended-code') {
        this.isValidRecommendedCode =
          this.recommendedCode !== null && this.recommendedCode.length === recommendedCodeLength
            ? false
            : null;
      } else {
        alert('로그인 상태이거나 회원가입 양식이 잘못 되어 가입하지 못했습니다.');
      }
    }
  }
  async submit() {
    this.$validator.validateAll().then((result: boolean) => {
      if (!result) {
        return;
      }

      this.passPromotionCode = true;
      this.checkPromotionCode()
        .then((res: any) => {
          this.passPromotionCode = true;
          this.doSignup();
          return;
        })
        .catch((err: any) => {
          if (confirm(
            `이미 사용 중이거나 존재하지 않거나 유효하지 않은 쿠폰입니다.
            쿠폰 없이 가입신청을 계속 진행하시겠습니까?`)) {
            this.passPromotionCode = true;
            this.promotionCode = '';
            this.doSignup();
          }
        });
    });
  }

  async checkRecommendedCode($event: Event) {
    const value = ($event.target as HTMLInputElement).value;
    if (value.length !== recommendedCodeLength) {
      this.isValidRecommendedCode = null;
      return;
    }
    try {
      await this.checkRecommendedCodeAction(value);
      this.isValidRecommendedCode = true;
    } catch (e) {
      this.isValidRecommendedCode = false;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
@import '~@/assets/styles/icons.scss';

.signup__title {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 10px 0 0;
}
.form__signup {
  padding: 30px 31px;
}
.form-control {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 0;

  .wrapper {
    width: 100%;
    box-sizing: border-box;
    padding: 5px 0;
    text-align: left;
  }

  &.form-control__buttons {
    position: fixed;
    bottom: 30px;
    left: 0;
    padding: 0 31px;
    display: flex;
  }
}
.form__label {
  box-sizing: border-box;
  text-align: left;
  font-size: 0.875rem;
  font-weight: bold;
  color: #444;

  &.has-error {
    color: #f03d44;
  }
}
.form__input {
  width: 100%;
  box-sizing: border-box;
  border: none;
  border-bottom: 1px solid #ddd;
  padding: 10px 5px;

  &:focus {
    @include vendor-prefix(outline, 0);
  }

  &.recommended-code__valid {
  }
  &.recommended-code__invalid {
  }
}
.form__button {
  padding: 15px 0;
  flex-grow: 1;
  font-size: 1rem;
  border: none;

  &.button__cancel {
    background-color: transparent;
    margin-right: 2px;
    flex-grow: 1;
    font-size: 0.875rem;
    color: #9347a9;
  }
  &.button__submit {
    background-color: #9347a9;
    flex-grow: 3;
    color: #fff;
    font-weight: bold;
    @include vendor-prefix(border-radius, 50px);
  }
}
.form-errors {
  display: flex;
  padding: 6px 0;
  font-size: 0.75rem;
  color: #f03d44;
  align-items: center;

  .icon-warning { margin-right: 5px; }
}
</style>

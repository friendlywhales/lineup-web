<template>
  <div class="toppage-container">
    <div class="toppage__welcome">
      <h1 class="toppage__title">
        <span class="toppage__title-text">#LINEUP</span>
      </h1>

      <p class="welcome__message">지금 시작하세요!</p>

      <div class="toppage__nav">
        <router-link :to="{name: 'SignUp'}" class="nav__button button__enter">시작하기</router-link>
        <router-link :to="{name: 'Login'}" class="nav__button button__login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Getter } from 'vuex-class';

@Component({
  name: 'toppage',
  components: {
  },
})
export default class TopPage extends Vue {
  @Getter('isLoggedIn', { namespace: 'auth' }) isLoggedIn!: boolean;

  created() {
    if (this.isLoggedIn) {
      this.$router.replace({ name: 'Home' });
    }
  }
}
</script>

<style lang="scss">
@import '~@/assets/styles/base.scss';

.toppage-container {
  position: fixed;
  top: 0;
  left: 0;
  min-width: 100%;
  height: 100vh;
  background: url("/static/img/toppage-bg.jpg") no-repeat center center fixed;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;

  .toppage__welcome {
    width: 90%;
    @media #{$platform-pc} {
      width: $break-pc;
    }
    box-sizing: border-box;
    padding: 40px 0;
    background-color: rgba(255, 255, 255, .9);
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.5);
    text-align: center;
    @include vendor-prefix(border-radius, 8px);

    .toppage__title {
      display: flex;
      width: 100%;
      height: 46px;
      background: url("/static/img/lineup_banner.png") no-repeat center center;
      background-size: contain;
      text-align: center;

      .toppage__title-text {
        display: none;
        /*
        background-image: linear-gradient(to bottom, #de80bf, #834eb0);
        font-family: ArialRoundedMT;
        font-size: 2.5rem;
        font-weight: bold;
        font-style: normal;
        font-stretch: normal;
        line-height: normal;
        letter-spacing: -1px;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 auto;
        */
      }
    }

    .welcome__message {
      padding: 10px 0;
      color: #753887;
    }
  }

  .toppage__nav {
    display: flex;
    flex-direction: column;
    width: 100%;
    box-sizing: border-box;
    padding: 37px 21.2px 0;

    .nav__button {
      padding: 12px;
      box-sizing: border-box;
      font-weight: bold;
      font-size: 0.875rem;
      @include vendor-prefix(border-radius, 22px);
    }
    .button__enter {
      color: #fff;
      background-color: #9347a9;
      margin-bottom: 11px;
      font-weight: bold;
    }
    .button__login {
      border: 1px solid #9347a9;
      color: #9347a9;
      font-weight: 500;
      @include vendor-prefix(border-radius, 22px);
    }
  }
}
</style>

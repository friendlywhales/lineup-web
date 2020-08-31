<template>
  <div class="promotion-page">
    <h3 class="promotion-page__title">쿠폰 코드</h3>
    <form class="form" @submit.prevent="submit">
      <div class="form__control">
        <input type="text" id="promotion-code" required class="form__input"
               placeholder="쿠폰 코드를 입력하세요."
               v-model.trim="value">
      </div>

      <div class="form__control form__control-buttons">
        <button type="submit" class="form__button button__submit">등록</button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import PromotionCode from './scripts/promotion-code';
export default PromotionCode;
</script>

<style lang="scss">
@import '../assets/styles/base.scss';

.promotion-page {
  box-sizing: border-box;
  padding: 20px;
}
.promotion-page__title {
  font-size: 0.875rem;
  color: #444;
  text-align: left;
  padding-bottom: 11px;
}
.form {
  width: 100%;

  .form__control {
    width: 100%;
    box-sizing: border-box;
    display: flex;
    align-items: center;

    &.form__control-buttons {
      padding-top: 20px;
    }
  }
  .form__label {
    min-width: 7rem;
    max-width: 7rem;
    flex: 1 0 0;
  }
  .form__input {
    width: 100%;
    flex: 1 0 0;
    box-sizing: border-box;
    border: none;
    border-bottom: 1px solid #ddd;
    padding: 7px 5px;
    font-size: 0.875rem;

    @include placeholder {
      color: #888;
      font-size: 0.875rem;
    }
  }
  .form__button {
    width: 100%;
    padding: 10px 0;
    box-sizing: border-box;

    &.button__submit {
      font-size: 0.875rem;
      color: #fff;
      background-color: #9347a9;
      font-weight: bold;
      padding: 15px 0;
      @include vendor-prefix(border-radius, 100px);
    }
  }
}
</style>

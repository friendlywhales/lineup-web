<template>
  <div class="wallet-container" v-if="isUserinfoLoaded">
    <div class="lineup-wallet">
      <ul class="properties__list">
        <li class="properties__item" @click="toggleLineUpPoints">
          <div class="item__label">라인업 마일리지</div>
          <div class="item__value">
            {{ userinfo.lineup_points.total }}
            <i :class="['fas', {'fa-caret-down': !isToggleLineUpPoints}, {'fa-caret-up': isToggleLineUpPoints}]"></i>
          </div>
        </li>

        <li class="properties__item detail" v-show="isToggleLineUpPoints">
          <ul class="detail__container">
            <li class="properties__item" v-for="(value, key) in lineupPointsDetail">
              <div class="item__label">{{ getBehaviourNameByCode(key) }}</div>
              <div class="item__value">{{ value }}</div>
            </li>
          </ul>
        </li>
      </ul>
    </div>

    <div class="steem-wallet" v-if="isExistedsteemAccount && isSteemLoaded">
      <ul class="properties__list">
        <li class="properties__item">
          <div class="item__label">스팀</div>
          <div class="item__value">{{ steemCoin }}</div>
        </li>
        <li class="properties__item">
          <div class="item__label">스팀 달러</div>
          <div class="item__value">{{ steemDollar }}</div>
        </li>
        <li class="properties__item">
          <div class="item__label">스팀 파워</div>
          <div class="item__value">{{ steemPower }}</div>
        </li>
        <li class="properties__item">
          <div class="item__label">보팅 파워</div>
          <div class="item__value">{{ steemVotingPower }} %</div>
        </li>
      </ul>
    </div>
  </div>
  <div v-else>
    <loading-spinner></loading-spinner>
  </div>
</template>
<script lang="ts">
import Wallet from './scripts/wallet';
export default Wallet;
</script>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.wallet-container {
  padding: 20px;
}

.properties__list  {
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;

  .properties__item {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    box-sizing: border-box;
    border-bottom: 1px solid rgba(0, 0, 0, .6);

    &.detail {
      border: none;
      padding: 10px;
    }

    .item_label {
      flex-grow: 1;
      font-weight: bold;
    }
    .item_value {
      flex-grow: 1;
    }

    .detail__container {
      width: 100%;
    }
  }
}
</style>

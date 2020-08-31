import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import { NoCache } from '@/utils/components';
import * as T from '@/store/auth/types';
import * as cT from '@/store/contents/types';

const namespace = 'auth';

const behaviourNames = {
  posting: '포스팅',
  comment: '댓글',
  follow: '팔로워',
  login: '매일접속',
  signup: '회원가입',
  like: '좋아요',
};

@Component({
  name: 'wallet',
})
export default class Wallet extends Vue {
  isUserinfoLoaded: boolean = false;
  isExistedsteemAccount: boolean = true;
  isSteemLoaded: boolean = false;
  steemAccountInfo: any;
  steemDynamicGlobalProperties!: any;
  steemUsername: string = '';
  steemCoin: string = '';
  steemPower: string = '';
  steemDollar: string = '';
  steemVotingPower: string = '';
  isToggleLineUpPoints: boolean = false;

  @Action('fetchMyInfo', { namespace }) fetchMyInfo: any;
  @Action('fetchSteemAccountInfo', { namespace }) fetchSteemAccountInfo: any;
  @Action('fetchSteemDynamicGlobalProperties', { namespace })
  fetchSteemDynamicGlobalProperties: any;

  @Getter('userinfo', { namespace }) userinfo!: T.User;

  getSteemUsername(): string | undefined {
    if (!_.isObject(this.userinfo.social_auth)) { return undefined; }
    if (!_.has(this.userinfo.social_auth, 'steemconnect')) { return undefined; }
    return (this.userinfo.social_auth as any).steemconnect.username;
  }
  calculateSteemPower(): string {
    const [vs, text] = this.steemAccountInfo.vesting_shares.split(' ');
    const [tvfs, text2] = this.steemDynamicGlobalProperties.total_vesting_fund_steem.split(' ');
    const [tvs, text3] = this.steemDynamicGlobalProperties.total_vesting_shares.split(' ');
    const result =  Number.parseFloat(tvfs) * (Number.parseFloat(vs) / Number.parseFloat(tvs));

    return `${result.toPrecision(3)} SP`;
  }

  toggleLineUpPoints() {
    this.isToggleLineUpPoints = !this.isToggleLineUpPoints;
  }

  get lineupPointsDetail(): {[key: string]: number} {
    return _.pickBy(this.userinfo.lineup_points || {}, (v, k) => k !== 'total');
  }

  getBehaviourNameByCode(code: string): string {
    return _.get(behaviourNames, code, '이외');
  }

  async created() {
    await this.fetchMyInfo();
    this.isUserinfoLoaded = true;
    if (!this.getSteemUsername()) {
      this.isExistedsteemAccount = false;
      this.isSteemLoaded = false;
      return;
    }
    this.steemUsername = this.getSteemUsername() as string;

    const accountRes = await this.fetchSteemAccountInfo([this.steemUsername]);
    const propRes = await this.fetchSteemDynamicGlobalProperties();
    if (!accountRes.result || !propRes.result) {
      this.isExistedsteemAccount = false;
      this.isSteemLoaded = false;
      return;
    }

    this.steemAccountInfo = _.find(accountRes.result, { name: this.steemUsername });
    this.steemCoin = this.steemAccountInfo.balance;
    this.steemDollar = this.steemAccountInfo.sbd_balance;
    this.steemVotingPower = (this.steemAccountInfo.voting_power / 100).toPrecision(3);

    this.steemDynamicGlobalProperties = propRes.result;
    this.steemPower = this.calculateSteemPower();
    this.isExistedsteemAccount = true;
    this.isSteemLoaded = true;
  }
}

import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter } from 'vuex-class';

const namespace = 'auth';

@Component({ name: 'promotion-code' })
export default class PromotionCode extends Vue {
  @Action('consumePromotionCode', { namespace }) consumePromotionCode: any;

  value: string = '';

  submit() {
    if (!this.value) { return; }
    this.consumePromotionCode(this.value)
      .then((res: any) => {
        alert(`[${this.value}] 쿠폰을 등록 하였습니다.`);
        this.value = '';
        return;
      })
      .catch((err: any) => {
        alert('정상적이지 않은 쿠폰 번호입니다.\ncontact@line-up.me 로 문의하세요.');
        return;
      });
  }
}

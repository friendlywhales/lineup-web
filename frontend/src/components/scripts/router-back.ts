import Vue, { CreateElement, VNode } from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

@Component({ name: 'router-back' })
export default class RouterBack extends Vue {
  @Prop({ default: 'a' })
  tag!: string;

  render(this: any, h: CreateElement): VNode {
    const $root = this.$root;

    return h(
      this.tag,
      {
        attrs: Object.assign(
          {
            href: this.tag === 'a' ? 'javascript:' : null,
            type: this.tag === 'button' ? 'button' : null,
          },
          this.$attrs,
        ),
        on: {
          click() {
            $root.$router.back();
          },
        },
      },
      this.$slots.default,
    );
  }
}

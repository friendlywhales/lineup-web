
import Vue, { ComponentOptions } from 'vue';
import { createDecorator, VueDecorator } from 'vue-class-component';

export const NoCache = createDecorator((options: ComponentOptions<Vue>, key: string) => {
  (options as any).computed[key].cache = false;
});

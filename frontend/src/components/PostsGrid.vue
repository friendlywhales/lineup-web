<template>
  <div class="posts-grid__container">
    <div class="posts-grid__list" :key="`row-${index}`" v-for="(row, index) in rows">
      <each-post-grid :class="[`posts-grid__item--${row.length}-by-row`]"
                      :key="item.uid"
                      :post="item"
                      v-for="item in row"></each-post-grid>
      <div class="posts-grid__item posts-grid__item--hidden" :key="`empty-${index}`" v-for="(_, index) in getEmptyItems(row)"></div>
    </div>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Action, Getter, Mutation } from 'vuex-class';
import { Prop } from 'vue-property-decorator';
import * as cT from '@/store/contents/types';
import EachPostGrid from './EachPostGrid.vue';

const itemsPerRow = 3;
const namespace = 'contents';

@Component({
  name: 'posts-grid',
  components: {
    EachPostGrid,
  },
})
export default class PostsGrid extends Vue {
  @Prop()
  posts!: cT.Post[];

  get rows(): cT.Post[][] {
    return _.chunk(this.posts, itemsPerRow) as cT.Post[][];
  }

  getEmptyItems(row: cT.Post[]): any {
    return Array(itemsPerRow - row.length);
  }
}
</script>

<style lang="scss" scoped>
  .posts-grid__container {
    display: flex;
    flex-direction: column;
  }
  .posts-grid__list {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    margin-bottom: 3px;

    &:last-child { margin: 0; }

    .posts-grid__item {
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      margin-right: 3px;
      align-items: stretch;
      flex: 1 0 0;

      &:last-child { margin: 0; }
      &.posts-grid__item--hidden {
        visibility: hidden;
      }
    }
  }
</style>

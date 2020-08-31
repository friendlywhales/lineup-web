<template>
  <div class="collections-grid__container">
    <div class="collections-grid__list" :key="`row-${index}`" v-for="(row, index) in rows">
      <div
        :class="['collections-grid__item', `collections-grid__item--${row.length}-by-row`]"
        :key="item.uid"
        v-for="item in row">
        <router-link class="collections-grid__link" :to="{name: 'CollectionDetail', params: {uid: item.uid}}">
          <img :src="getTitleImage(item)" class="collections-grid__image" v-if="getTitleImage(item)">
          <div class="collections-grid__image no-image" v-if="!getTitleImage(item)">
            <i class="far fa-folder icon"></i>
          </div>
          <div class="collections-grid__name">{{ item.name }}</div>
        </router-link>
      </div>
      <div class="collections-grid__item collections-grid__item--hidden"
        :key="`empty-${index}`"
        v-for="(_, index) in getEmptyItems(row)"></div>
    </div>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';
import { Action, Getter } from 'vuex-class';
import * as T from '../store/contents/types';

const itemsPerRow = 3;

@Component({ name: 'collections-grid' })
export default class CollectionsGrid extends Vue {
  @Prop()
  collections!: T.ICollection[] | undefined;
  @Prop({ default: itemsPerRow })
  itemsPerRow!: number;

  get computedItemsPerRow(): number {
    return this.itemsPerRow === 0
      ? this.collections
        ? (this.collections as T.ICollection[]).length
        : this.itemsPerRow
      : this.itemsPerRow;
  }
  get rows(): T.ICollection[][] {
    return _.chunk(this.collections, this.computedItemsPerRow) as T.ICollection[][];
  }

  getTitleImage(item: T.ICollection): string | undefined {
    // todo: srcset 필요.
    if (item.title_images.length > 0) return item.title_images[0];
    return undefined;
  }
  getEmptyItems(row: T.ICollection[]): any {
    return Array(this.computedItemsPerRow - row.length);
  }
  created() {
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/styles/base.scss';

  .collections-grid__container {
    display: flex;
    flex-direction: column;
  }
  .collections-grid__list {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    margin-bottom: 3px;

    &:last-child { margin: 0; }

    .collections-grid__item {
      color: rgba(0, 0, 0, .6);
      width: 100%;
      height: 100%;
      /*min-width: 180px;*/
      /*min-height: 180px;*/
      /*max-width: 50%;*/
      box-sizing: border-box;
      margin-right: 3px;
      align-items: stretch;
      flex: 1 0 0;

      &:last-child { margin: 0; }
    }

    .collections-grid__link {
      position: relative;
      display: block;
      width: 100%;
      height: 100%;

      .collections-grid__name {
        position: absolute;
        z-index: 10;
        left: 0;
        bottom: 0;
        width: 100%;
        font-size: 0.875rem;
        text-align: center;
        padding: 5px 0;
        box-sizing: border-box;
        background-color: rgba(109, 46, 126, .9);
        color: #fff;
      }
    }
    .collections-grid__image {
      display: block;
      width: 100%;
      height: 100%;

      &.no-image {
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(0, 0, 0, .6);
        box-sizing: border-box;
        @include vendor-prefix(border-radius, 10px);

        .icon {
          transform: scale(2.0);
        }
      }
    }
  }
</style>

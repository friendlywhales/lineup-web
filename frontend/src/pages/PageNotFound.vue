<script lang="ts">
import Component from "vue-class-component";
import ErrorPage, { errors } from './ErrorPage.vue';

@Component({ name: 'page-not-found' })
export default class PageNotFound extends ErrorPage {
  created() {
    this.error = errors['page-not-found'];
  }
}
</script>

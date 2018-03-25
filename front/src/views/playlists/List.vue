<template>
  <div>
    <div class="ui vertical stripe segment">
      <h2 class="ui header">Browsing playlists</h2>
      <div :class="['ui', {'loading': isLoading}, 'form']">
        <template v-if="$store.state.auth.authenticated">
          <button
            @click="$store.commit('playlists/chooseTrack', null)"
            class="ui basic green button">Manage your playlists</button>
          <div class="ui hidden divider"></div>
        </template>
        <div class="fields">
          <div class="field">
            <label>Search</label>
            <input type="text" v-model="query" placeholder="Enter an playlist name..."/>
          </div>
          <div class="field">
            <label>Ordering</label>
            <select class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ option[1] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label>Ordering direction</label>
            <select class="ui dropdown" v-model="orderingDirection">
              <option value="">Ascending</option>
              <option value="-">Descending</option>
            </select>
          </div>
          <div class="field">
            <label>Results per page</label>
            <select class="ui dropdown" v-model="paginateBy">
              <option :value="parseInt(12)">12</option>
              <option :value="parseInt(25)">25</option>
              <option :value="parseInt(50)">50</option>
            </select>
          </div>
        </div>
      </div>
      <div class="ui hidden divider"></div>
      <playlist-card-list v-if="result" :playlists="result.results"></playlist-card-list>
      <div class="ui center aligned basic segment">
        <pagination
          v-if="result && result.results.length > 0"
          @page-changed="selectPage"
          :current="page"
          :paginate-by="paginateBy"
          :total="result.count"
          ></pagination>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'
import $ from 'jquery'

import OrderingMixin from '@/components/mixins/Ordering'
import PaginationMixin from '@/components/mixins/Pagination'
import PlaylistCardList from '@/components/playlists/CardList'
import Pagination from '@/components/Pagination'

const FETCH_URL = 'playlists/'

export default {
  mixins: [OrderingMixin, PaginationMixin],
  props: {
    defaultQuery: {type: String, required: false, default: ''}
  },
  components: {
    PlaylistCardList,
    Pagination
  },
  data () {
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || '-creation_date')
    return {
      isLoading: true,
      result: null,
      page: parseInt(this.defaultPage),
      query: this.defaultQuery,
      paginateBy: parseInt(this.defaultPaginateBy || 12),
      orderingDirection: defaultOrdering.direction,
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['creation_date', 'Creation date'],
        ['modification_date', 'Last modification date'],
        ['name', 'Name']
      ]
    }
  },
  created () {
    this.fetchData()
  },
  mounted () {
    $('.ui.dropdown').dropdown()
  },
  methods: {
    updateQueryString: _.debounce(function () {
      this.$router.replace({
        query: {
          query: this.query,
          page: this.page,
          paginateBy: this.paginateBy,
          ordering: this.getOrderingAsString()
        }
      })
    }, 500),
    fetchData: _.debounce(function () {
      var self = this
      this.isLoading = true
      let url = FETCH_URL
      let params = {
        page: this.page,
        page_size: this.paginateBy,
        q: this.query,
        ordering: this.getOrderingAsString()
      }
      axios.get(url, {params: params}).then((response) => {
        self.result = response.data
        self.isLoading = false
      })
    }, 500),
    selectPage: function (page) {
      this.page = page
    }
  },
  watch: {
    page () {
      this.updateQueryString()
      this.fetchData()
    },
    paginateBy () {
      this.updateQueryString()
      this.fetchData()
    },
    ordering () {
      this.updateQueryString()
      this.fetchData()
    },
    orderingDirection () {
      this.updateQueryString()
      this.fetchData()
    },
    query () {
      this.updateQueryString()
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
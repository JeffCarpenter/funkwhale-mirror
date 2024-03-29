<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">
        <translate translate-context="Content/Artist/Title">Browsing artists</translate>
      </h2>
      <form :class="['ui', {'loading': isLoading}, 'form']" @submit.prevent="updatePage();updateQueryString();fetchData()">
        <div class="fields">
          <div class="field">
            <label for="artist-search">
              <translate translate-context="Content/Search/Input.Label/Noun">Artist name</translate>
            </label>
            <div class="ui action input">
              <input id="artist-search" type="text" name="search" v-model="query" :placeholder="labels.searchPlaceholder"/>
              <button class="ui icon button" type="submit" :aria-label="$pgettext('Content/Search/Input.Label/Noun', 'Search')">
                <i class="search icon"></i>
              </button>
            </div>
          </div>
          <div class="field">
            <label for="tags-search"><translate translate-context="*/*/*/Noun">Tags</translate></label>
            <tags-selector v-model="tags"></tags-selector>
          </div>
          <div class="field">
            <label for="artist-ordering"><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering</translate></label>
            <select id="artist-ordering" class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ sharedLabels.filters[option[1]] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label for="artist-ordering-direction"><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering direction</translate></label>
            <select id="artist-ordering-direction" class="ui dropdown" v-model="orderingDirection">
              <option value="+"><translate translate-context="Content/Search/Dropdown">Ascending</translate></option>
              <option value="-"><translate translate-context="Content/Search/Dropdown">Descending</translate></option>
            </select>
          </div>
          <div class="field">
            <label for="artist-results"><translate translate-context="Content/Search/Dropdown.Label/Noun">Results per page</translate></label>
            <select id="artist-results" class="ui dropdown" v-model="paginateBy">
              <option :value="parseInt(12)">12</option>
              <option :value="parseInt(30)">30</option>
              <option :value="parseInt(50)">50</option>
            </select>
          </div>
          <div class="field">
            <span id="excludeHeader">Exclude Compilation Artists</span>
              <div id="excludeCompilation" class="ui toggle checkbox">
              <input id="exclude-compilation" v-model="excludeCompilation" true-value="true" false-value="null" type="checkbox">
              <label for="exclude-compilation" class="visually-hidden"><translate translate-context="Content/Search/Checkbox/Noun">Exclude Compilation Artists</translate></label>
            </div>
          </div>
        </div>
      </form>
      <div class="ui hidden divider"></div>
      <div v-if="result && result.results.length > 0" class="ui five app-cards cards">
        <div v-if="isLoading" class="ui inverted active dimmer">
          <div class="ui loader"></div>
        </div>
        <artist-card :artist="artist" v-for="artist in result.results" :key="artist.id"></artist-card>
      </div>
      <div v-else-if="!isLoading" class="ui placeholder segment sixteen wide column" style="text-align: center; display: flex; align-items: center">
        <div class="ui icon header">
          <i class="compact disc icon"></i>
          <translate translate-context="Content/Artists/Placeholder">
            No results matching your query
          </translate>
        </div>
        <router-link
          v-if="$store.state.auth.authenticated"
          :to="{name: 'content.index'}"
          class="ui success button labeled icon">
          <i class="upload icon"></i>
          <translate translate-context="Content/*/Verb">
              Add some music
          </translate>
        </router-link>
      </div>
      <div class="ui center aligned basic segment">
        <pagination
          v-if="result && result.count > paginateBy"
          @page-changed="selectPage"
          :current="page"
          :paginate-by="paginateBy"
          :total="result.count"
          ></pagination>
      </div>
    </section>
  </main>
</template>

<script>
import qs from 'qs'
import axios from "axios"
import _ from "@/lodash"
import $ from "jquery"

import logger from "@/logging"

import OrderingMixin from "@/components/mixins/Ordering"
import PaginationMixin from "@/components/mixins/Pagination"
import TranslationsMixin from "@/components/mixins/Translations"
import ArtistCard from "@/components/audio/artist/Card"
import Pagination from "@/components/Pagination"
import TagsSelector from '@/components/library/TagsSelector'

const FETCH_URL = "artists/"

export default {
  mixins: [OrderingMixin, PaginationMixin, TranslationsMixin],
  props: {
    defaultQuery: { type: String, required: false, default: "" },
    defaultTags: { type: Array, required: false, default: () => { return [] } },
    scope: { type: String, required: false, default: "all" },
  },
  components: {
    ArtistCard,
    Pagination,
    TagsSelector,
  },
  data() {
    return {
      isLoading: true,
      result: null,
      excludeCompilation: true,
      page: parseInt(this.defaultPage),
      query: this.defaultQuery,
      tags: (this.defaultTags || []).filter((t) => { return t.length > 0 }),
      orderingOptions: [["creation_date", "creation_date"], ["name", "name"]]
    }
  },
  created() {
    this.fetchData()
  },
  mounted() {
    $(".ui.dropdown").dropdown()
  },
  computed: {
    labels() {
      let searchPlaceholder = this.$pgettext('Content/Search/Input.Placeholder', "Search…")
      let title = this.$pgettext('*/*/*/Noun', "Artists")
      return {
        searchPlaceholder,
        title
      }
    }
  },
  methods: {
    updateQueryString: function() {
      history.pushState(
        {},
        null,
        this.$route.path + '?' + new URLSearchParams(
          {
          query: this.query,
          page: this.page,
          tag: this.tags,
          paginateBy: this.paginateBy,
          ordering: this.getOrderingAsString(),
          content_category: 'music',
          include_channels: true,
        }).toString()
      )
    },
    fetchData: function() {
      var self = this
      this.isLoading = true
      let url = FETCH_URL
      let params = {
        scope: this.scope,
        page: this.page,
        page_size: this.paginateBy,
        has_albums: this.excludeCompilation,
        q: this.query,
        ordering: this.getOrderingAsString(),
        playable: "true",
        tag: this.tags,
        include_channels: "true",
        content_category: 'music',
      }
      logger.default.debug("Fetching artists")
      axios.get(
        url,
        {
          params: params,
          paramsSerializer: function(params) {
            return qs.stringify(params, { indices: false })
          }
        }
      ).then(response => {
        self.result = response.data
        self.isLoading = false
      }, error => {
        self.result = null
        self.isLoading = false
      })
    },
    selectPage: function(page) {
      this.page = page
    },
    updatePage() {
      this.page = this.defaultPage
    }
  },
  watch: {
    page() {
      this.updateQueryString()
      this.fetchData()
    },
    "$store.state.moderation.lastUpdate": function () {
      this.fetchData()
    },
    excludeCompilation() {
      this.fetchData()
    }
  }
}
</script>

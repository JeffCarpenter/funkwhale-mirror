<template>
  <div class="channel-serie-card">
    <div class="two-images">
      <img alt="" @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-if="cover && cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](cover.urls.medium_square_crop)">
      <img alt="" @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-else src="../../assets/audio/default-cover.png">
      <img alt="" @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-if="cover && cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](cover.urls.medium_square_crop)">
      <img alt="" @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-else src="../../assets/audio/default-cover.png">
    </div>
    <div class="content ellipsis">
      <strong>
        <router-link class="discrete link" :to="{name: 'library.albums.detail', params: {id: serie.id}}">
          {{ serie.title }}
        </router-link>
      </strong>
      <div class="description">
        <translate translate-context="Content/Channel/Paragraph"
          translate-plural="%{ count } episodes"
          :translate-n="serie.tracks_count"
          :translate-params="{count: serie.tracks_count}">
          %{ count } episode
        </translate>
      </div>
    </div>
    <div class="controls">
      <play-button :icon-only="true" :is-playable="true" :button-classes="['ui', 'circular', 'vibrant', 'icon', 'button']" :album="serie"></play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['serie'],
  components: {
    PlayButton,
  },
  computed: {
    cover () {
      if (this.serie.cover) {
        return this.serie.cover
      }
    },
    duration () {
      let uploads = this.serie.uploads.filter((e) => {
        return e.duration
      })
      return uploads[0].duration
    }
  }
}
</script>

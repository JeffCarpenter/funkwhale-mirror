<template>
  <div :class="[{active: currentTrack && isPlaying && entry.id === currentTrack.id}, 'channel-entry-card']">
    <div class="controls">
      <play-button class="basic circular icon" :discrete="true" :icon-only="true" :is-playable="true" :button-classes="['ui', 'circular', 'inverted vibrant', 'icon', 'button']" :track="entry"></play-button>
    </div>
    <img
      @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})"
      alt=""
      class="channel-image image"
      v-if="cover && cover.urls.original"
      v-lazy="$store.getters['instance/absoluteUrl'](cover.urls.medium_square_crop)">
    <img
      @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})"
      class="channel-image image"
      v-else-if="entry.artist.content_category === 'podcast' && defaultCover != undefined"
      v-lazy="$store.getters['instance/absoluteUrl'](defaultCover.urls.medium_square_crop)">
    <img
      @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})"
      alt=""
      class="channel-image image"
      v-else-if="entry.album && entry.album.cover && entry.album.cover.urls.original"
      v-lazy="$store.getters['instance/absoluteUrl'](entry.album.cover.urls.medium_square_crop)">
    <img
      @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})"
      alt=""
      class="channel-image image"
      v-else
      src="../../assets/audio/default-cover.png">
    <div class="ellipsis content">
      <strong>
        <router-link class="discrete link" :to="{name: 'library.tracks.detail', params: {id: entry.id}}">
          {{ entry.title }}
        </router-link>
      </strong>
      <br>
      <human-date class="really discrete" :date="entry.creation_date"></human-date>
    </div>
    <div class="meta">
        <template v-if="$store.state.auth.authenticated && $store.getters['favorites/isFavorite'](entry.id)">
          <track-favorite-icon class="tiny" :track="entry"></track-favorite-icon>
        </template>
        <human-duration v-if="duration" :duration="duration"></human-duration>
    </div>
    <div class="controls">
      <play-button class="play-button basic icon" :dropdown-only="true" :is-playable="entry.is_playable" :dropdown-icon-classes="['ellipsis', 'vertical', 'large really discrete']" :track="entry"></play-button>      
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import { mapGetters } from "vuex"


export default {
  props: ['entry', 'defaultCover'],
  components: {
    PlayButton,
    TrackFavoriteIcon,
  },
  computed: {

    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),

    isPlaying () {
      return this.$store.state.player.playing
    },
    cover () {
      if (this.entry.cover) {
        return this.entry.cover
      }
    },
    duration () {
      let uploads = this.entry.uploads.filter((e) => {
        return e.duration
      })
      if (uploads.length > 0) {
        return uploads[0].duration
      }
    }
  }
}
</script>

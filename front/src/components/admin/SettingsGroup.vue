<template>
  <form :id="group.id" class="ui form" @submit.prevent="save">
    <div class="ui divider" />
    <h3 class="ui header">{{ group.label }}</h3>
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header">{{ $t('Error while saving settings') }}</div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div v-if="result" class="ui positive message">
      {{ $t('Settings updated successfully.') }}
    </div>
    <p v-if="group.help">{{ group.help }}</p>
    <div v-for="setting in settings" class="ui field">
      <template v-if="setting.field.widget.class !== 'CheckboxInput'">
        <label :for="setting.identifier">{{ setting.verbose_name }}</label>
        <p v-if="setting.help_text">{{ setting.help_text }}</p>
      </template>
      <input
        :id="setting.identifier"
        v-if="setting.field.widget.class === 'PasswordInput'"
        type="password"
        class="ui input"
        v-model="values[setting.identifier]" />
      <input
        :id="setting.identifier"
        v-if="setting.field.widget.class === 'TextInput'"
        type="text"
        class="ui input"
        v-model="values[setting.identifier]" />
      <input
        :id="setting.identifier"
        v-if="setting.field.class === 'IntegerField'"
        type="number"
        class="ui input"
        v-model.number="values[setting.identifier]" />
      <textarea
        :id="setting.identifier"
        v-else-if="setting.field.widget.class === 'Textarea'"
        type="text"
        class="ui input"
        v-model="values[setting.identifier]" />
      <div v-else-if="setting.field.widget.class === 'CheckboxInput'" class="ui toggle checkbox">
        <input
          :id="setting.identifier"
          :name="setting.identifier"
          v-model="values[setting.identifier]"
          type="checkbox" />
        <label :for="setting.identifier">{{ setting.verbose_name }}</label>
        <p v-if="setting.help_text">{{ setting.help_text }}</p>
      </div>
    </div>
    <button
      type="submit"
      :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']">
        {{ $t('Save') }}
    </button>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    group: {type: Object, required: true},
    settingsData: {type: Array, required: true}
  },
  data () {
    return {
      values: {},
      result: null,
      errors: [],
      isLoading: false
    }
  },
  created () {
    let self = this
    this.settings.forEach(e => {
      self.values[e.identifier] = e.value
    })
  },
  methods: {
    save () {
      let self = this
      this.isLoading = true
      self.errors = []
      self.result = null
      axios.post('instance/admin/settings/bulk/', self.values).then((response) => {
        self.result = true
        self.isLoading = false
        self.$store.dispatch('instance/fetchSettings')
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    settings () {
      let byIdentifier = {}
      this.settingsData.forEach(e => {
        byIdentifier[e.identifier] = e
      })
      return this.group.settings.map(e => {
        return byIdentifier[e]
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.ui.checkbox p {
  margin-top: 1rem;
}
</style>
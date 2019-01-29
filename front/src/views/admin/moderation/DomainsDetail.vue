<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">
      <section :class="['ui', 'head', 'vertical', 'stripe', 'segment']" v-title="object.name">
        <div class="ui stackable two column grid">
          <div class="ui column">
            <div class="segment-content">
              <h2 class="ui header">
                <i class="circular inverted cloud icon"></i>
                <div class="content">
                  {{ object.name }}
                  <div class="sub header">
                    <a :href="externalUrl" target="_blank" rel="noopener noreferrer" class="logo-wrapper">
                      <translate>Open website</translate>&nbsp;
                      <i class="external icon"></i>
                    </a>
                  </div>
                </div>
              </h2>
            </div>
          </div>
          <div class="ui column">
            <div class="ui compact clearing placeholder segment">
              <template v-if="isLoadingPolicy">
                <div class="paragraph">
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
              </template>
              <template v-else-if="!policy && !showPolicyForm">
                <header class="ui header">
                  <h3>
                    <i class="shield icon"></i>
                    <translate>You don't have any rule in place for this domain.</translate>
                  </h3>
                </header>
                <p><translate>Moderation policies help you control how your instance interact with a given domain or account.</translate></p>
                <button @click="showPolicyForm = true" class="ui primary button">Add a moderation policy</button>
              </template>
              <instance-policy-card v-else-if="policy && !showPolicyForm" :object="policy" @update="showPolicyForm = true">
                <header class="ui header">
                  <h3>
                    <translate>This domain is subject to specific moderation rules</translate>
                  </h3>
                </header>
              </instance-policy-card>
              <instance-policy-form
                v-else-if="showPolicyForm"
                @cancel="showPolicyForm = false"
                @save="updatePolicy"
                @delete="policy = null; showPolicyForm = false"
                :object="policy"
                type="domain"
                :target="object.name" />
            </div>
          </div>
        </div>
      </section>
      <div class="ui vertical stripe segment">
        <div class="ui stackable three column grid">
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="info icon"></i>
                <div class="content">
                  <translate>Instance data</translate>
                </div>
              </h3>
              <table class="ui very basic table">
                <tbody>
                  <tr>
                    <td>
                      <translate>First seen</translate>
                    </td>
                    <td>
                      <human-date :date="object.creation_date"></human-date>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Last checked</translate>
                    </td>
                    <td>
                      <human-date v-if="object.nodeinfo_fetch_date" :date="object.nodeinfo_fetch_date"></human-date>
                      <translate v-else>N/A</translate>
                    </td>
                  </tr>

                  <template v-if="object.nodeinfo && object.nodeinfo.status === 'ok'">
                    <tr>
                      <td>
                        <translate>Software</translate>
                      </td>
                      <td>
                        {{ lodash.get(object, 'nodeinfo.payload.software.name', $gettext('N/A')) }} ({{ lodash.get(object, 'nodeinfo.payload.software.version', $gettext('N/A')) }})
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <translate>Name</translate>
                      </td>
                      <td>
                        {{ lodash.get(object, 'nodeinfo.payload.metadata.nodeName', $gettext('N/A')) }}
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <translate>Total users</translate>
                      </td>
                      <td>
                        {{ lodash.get(object, 'nodeinfo.payload.usage.users.total', $gettext('N/A')) }}
                      </td>
                    </tr>
                  </template>
                  <template v-if="object.nodeinfo && object.nodeinfo.status === 'error'">
                    <tr>
                      <td>
                        <translate>Status</translate>
                      </td>
                      <td>
                        <translate>Error while fetching node info</translate>&nbsp;

                        <span :data-tooltip="object.nodeinfo.error"><i class="question circle icon"></i></span>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
              <ajax-button @action-done="refreshNodeInfo" method="get" :url="'manage/federation/domains/' + object.name + '/nodeinfo/'">
                <translate>Refresh node info</translate>
              </ajax-button>
            </section>
          </div>
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="feed icon"></i>
                <div class="content">
                  <translate>Activity</translate>&nbsp;
                  <span :data-tooltip="labels.statsWarning"><i class="question circle icon"></i></span>

                </div>
              </h3>
              <div v-if="isLoadingStats" class="ui placeholder">
                <div class="full line"></div>
                <div class="short line"></div>
                <div class="medium line"></div>
                <div class="long line"></div>
              </div>
              <table v-else class="ui very basic table">
                <tbody>
                  <tr>
                    <td>
                      <router-link
                        :to="{name: 'manage.moderation.accounts.list', query: {q: 'domain:' + object.name }}">
                        <translate>Known accounts</translate>
                        </router-link>

                    </td>
                    <td>
                      {{ stats.actors }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Emitted messages</translate>
                    </td>
                    <td>
                      {{ stats.outbox_activities}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Received library follows</translate>
                    </td>
                    <td>
                      {{ stats.received_library_follows}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Emitted library follows</translate>
                    </td>
                    <td>
                      {{ stats.emitted_library_follows}}
                    </td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="music icon"></i>
                <div class="content">
                  <translate>Audio content</translate>&nbsp;
                  <span :data-tooltip="labels.statsWarning"><i class="question circle icon"></i></span>

                </div>
              </h3>
              <div v-if="isLoadingStats" class="ui placeholder">
                <div class="full line"></div>
                <div class="short line"></div>
                <div class="medium line"></div>
                <div class="long line"></div>
              </div>
              <table v-else class="ui very basic table">
                <tbody>
                  <tr>
                    <td>
                      <translate>Cached size</translate>
                    </td>
                    <td>
                      {{ stats.media_downloaded_size | humanSize }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Total size</translate>
                    </td>
                    <td>
                      {{ stats.media_total_size | humanSize }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Libraries</translate>
                    </td>
                    <td>
                      {{ stats.libraries }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Uploads</translate>
                    </td>
                    <td>
                      {{ stats.uploads }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Artists</translate>
                    </td>
                    <td>
                      {{ stats.artists }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Albums</translate>
                    </td>
                    <td>
                      {{ stats.albums}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate>Tracks</translate>
                    </td>
                    <td>
                      {{ stats.tracks }}
                    </td>
                  </tr>
                </tbody>
              </table>

            </section>
          </div>
        </div>
      </div>

    </template>
  </main>
</template>

<script>
import axios from "axios"
import logger from "@/logging"
import lodash from '@/lodash'

import InstancePolicyForm from "@/components/manage/moderation/InstancePolicyForm"
import InstancePolicyCard from "@/components/manage/moderation/InstancePolicyCard"

export default {
  props: ["id"],
  components: {
    InstancePolicyForm,
    InstancePolicyCard,
  },
  data() {
    return {
      lodash,
      isLoading: true,
      isLoadingStats: false,
      isLoadingPolicy: false,
      policy: null,
      object: null,
      stats: null,
      showPolicyForm: false,
      permissions: [],
    }
  },
  created() {
    this.fetchData()
    this.fetchStats()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      let url = "manage/federation/domains/" + this.id + "/"
      axios.get(url).then(response => {
        self.object = response.data
        self.isLoading = false
        if (self.object.instance_policy) {
          self.fetchPolicy(self.object.instance_policy)
        }
      })
    },
    fetchStats() {
      var self = this
      this.isLoadingStats = true
      let url = "manage/federation/domains/" + this.id + "/stats/"
      axios.get(url).then(response => {
        self.stats = response.data
        self.isLoadingStats = false
      })
    },
    fetchPolicy(id) {
      var self = this
      this.isLoadingPolicy = true
      let url = `manage/moderation/instance-policies/${id}/`
      axios.get(url).then(response => {
        self.policy = response.data
        self.isLoadingPolicy = false
      })
    },
    refreshNodeInfo (data) {
      this.object.nodeinfo = data
      this.object.nodeinfo_fetch_date = new Date()
    },
    updatePolicy (policy) {
      this.policy = policy
      this.showPolicyForm = false
    }
  },
  computed: {
    labels() {
      return {
        statsWarning: this.$gettext("Statistics are computed from known activity and content on your instance, and do not reflect general activity for this domain")
      }
    },
    externalUrl () {
      return `https://${this.object.name}`
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.placeholder.segment {
  width: 100%;
}
</style>
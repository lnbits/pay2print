window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      pay2printDialog: {
        show: false,
        data: {}
      },
      pay2printData: []
    }
  },
  methods: {
    submitForm() {
      LNbits.api
        .request(
          this.pay2printDialog.data.id ? 'PUT' : 'POST',
          '/pay2print/api/v1/print',
          this.g.user.wallets[0].adminkey,
          this.pay2printDialog.data
        )
        .then(_ => {
          this.getPay2Prints()
          this.pay2printDialog.show = false
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getPay2Prints() {
      LNbits.api
        .request('GET', '/pay2print/api/v1/print', this.g.user.wallets[0].inkey)
        .then(response => {
          this.pay2printData = response.data
        })
        .catch(LNbits.utils.notifyApiError)
    }
  },
  created() {
    this.getPay2Prints()
  }
})

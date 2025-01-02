window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      invoice: null,
      invoiceAmount: `${amount} sat per print`,
      paid: false
    }
  },
  methods: {
    reset() {
      this.invoice = null
      this.paid = false
    },
    uploaded(e) {
      const data = JSON.parse(e.xhr.response)
      this.invoice = data.payment_request
      const ws = new WebSocket(`${websocketUrl}/${data.payment_hash}`)
      ws.onmessage = ev => {
        const data = JSON.parse(ev.data)
        if (data.pending === false) {
          this.paid = true
          ws.close()
        }
      }
    }
  }
})

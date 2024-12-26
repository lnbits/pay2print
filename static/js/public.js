window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      invoice: null,
      invoiceAmount: amount + ' sat',
      paid: false
    }
  },
  methods: {
    uploaded(e) {
      console.log('uploaded', e.xhr)
      this.invoice = e.xhr.response
    }
  },
  created() {}
})

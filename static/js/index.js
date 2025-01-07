window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      printerUrl: '/pay2print/api/v1/printer',
      printUrl: '/pay2print/api/v1/print',
      printer: null,
      printerLabel: null,
      printers: [],
      prints: [],
      printsTable: {
        columns: [
          {
            name: 'payment_hash',
            align: 'left',
            label: 'payment_hash',
            field: 'payment_hash'
          },
          {
            name: 'file',
            align: 'left',
            label: 'file',
            field: 'file'
          },
          {
            name: 'print_status',
            align: 'left',
            label: 'print_status',
            field: 'print_status'
          },
          {
            name: 'payment_status',
            align: 'left',
            label: 'payment_status',
            field: 'payment_status'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      printersTable: {
        columns: [
          {
            name: 'name',
            align: 'left',
            label: 'name',
            field: 'name'
          },
          {
            name: 'host',
            align: 'left',
            label: 'host',
            field: 'host'
          },
          {
            name: 'id',
            align: 'left',
            label: 'id',
            field: 'id'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      printerDialog: {
        show: false,
        data: {}
      },
      qrDialog: {
        show: false,
        data: {}
      }
    }
  },
  methods: {
    submitPrinterForm() {
      const method = this.printerDialog.data.id ? 'PUT' : 'POST'
      const url = this.printerDialog.data.id
        ? `${this.printerUrl}/${this.printerDialog.data.id}`
        : this.printerUrl
      LNbits.api
        .request(
          method,
          url,
          this.g.user.wallets[0].adminkey,
          this.printerDialog.data
        )
        .then(_ => {
          this.getPrinters()
          this.printerDialog.show = false
          this.printerDialog.data = {}
        })
        .catch(LNbits.utils.notifyApiError)
    },
    openUpdatePrinter(printer_id) {
      const printer = this.printers.find(printer => printer.id === printer_id)
      this.printerDialog.data = {...printer}
      this.printerDialog.show = true
    },
    openLnurlQrCode(printer_id) {
        // const printer = this.printers.find(printer => printer.id === printer_id)
        const lnurl = `${window.location.origin}/pay2print/api/v1/lnurl/${printer_id}`
        this.qrDialog.data = { lnurl: lnurl }
        this.qrDialog.show = true
    },
    openFile(payment_hash) {
      return `/pay2print/api/v1/file/${payment_hash}`
    },
    getPrints(printer_id) {
      LNbits.api
        .request(
          'GET',
          `${this.printUrl}/${printer_id}`,
          this.g.user.wallets[0].inkey
        )
        .then(response => {
          this.prints = response.data
        })
        .catch(LNbits.utils.notifyApiError)
    },
    testPrinter(printer_id) {
      LNbits.api
        .request(
          'GET',
          `${this.printerUrl}/check/${printer_id}`,
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          console.log(response)
          Quasar.Notify.create({
            message: 'Printer check successful',
            color: 'positive'
          })
        })
        .catch(LNbits.utils.notifyApiError)
    },
    openPrint(print_id) {
      LNbits.api
        .request(
          'GET',
          `${this.printUrl}/print/${print_id}`,
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          this.prints = response.data
        })
        .catch(LNbits.utils.notifyApiError)
    },
    deletePrint(id) {
      LNbits.api
        .request(
          'DELETE',
          `${this.printUrl}/${id}`,
          this.g.user.wallets[0].adminkey
        )
        .then(_ => {
          this.getPrints(this.printer)
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getPrinters() {
      LNbits.api
        .request('GET', this.printerUrl, this.g.user.wallets[0].inkey)
        .then(response => {
          this.printers = response.data
          if (this.printers.length > 0) {
            this.printer = this.printers[0].id
            this.printerLabel = this.printers[0].name
          }
        })
        .catch(LNbits.utils.notifyApiError)
    },
    deletePrinter(id) {
      LNbits.api
        .request(
          'DELETE',
          `${this.printerUrl}/${id}`,
          this.g.user.wallets[0].adminkey
        )
        .then(_ => {
          this.getPrinters()
        })
        .catch(LNbits.utils.notifyApiError)
    }
  },
  watch: {
    printer(val) {
      if (val) {
        const printer = this.printers.find(printer => printer.id === val)
        this.printerLabel = printer.name
        this.getPrints(val)
      }
    }
  },
  created() {
    this.getPrinters()
  }
})

window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      uploadUrl: `/pay2print/api/v1/upload/${printer_id}`,
      invoice: null,
      invoiceAmount: `${amount} sat per print`,
      paid: false,
      webcam: false,
      picture: null,
      webcamError: ''
    }
  },
  mounted() {
    if (this.$refs.cameraStream) {
      navigator.mediaDevices
        .getUserMedia({
          video: {FacingMode: {exact: 'environment'}},
          audio: false
        })
        .then(stream => {
          this.webcam = true
          this.$refs.cameraStream.style.display = 'block'
          this.$refs.cameraStream.srcObject = stream
          this.$refs.cameraStream.play()
        })
        .catch(err => {
          this.webcam = false
          this.webcamError = err
        })
    }
  },
  methods: {
    takePicture() {
      this.picture = true
      this.webcam = false
      this.$refs.cameraStream.style.display = 'none'
      this.$refs.canvas.width = this.$refs.cameraStream.videoWidth
      this.$refs.canvas.height = this.$refs.cameraStream.videoHeight
      this.$refs.canvas
        .getContext('2d')
        .drawImage(this.$refs.cameraStream, 0, 0)
    },
    uploadPicture() {
      this.$refs.canvas.toBlob(blob => {
        const formData = new FormData()
        formData.append('file', blob, 'photobox.jpg')
        axios
          .post(this.uploadUrl, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          .then(response => {
            this.invoice = response.data.payment_request
            this.onPaid(response.data.payment_hash)
            Quasar.Notify.create({
              color: 'positive',
              message: 'Image uploaded successfully'
            })
            this.$refs.canvas.width = 0
            this.$refs.canvas.height = 0
          })
          .catch(LNbits.utils.notifyApiError)
      }, 'image/jpeg')
    },
    reset() {
      this.picture = false
      this.webcam = true
      if (this.$refs.canvas) {
        this.$refs.canvas.width = 0
        this.$refs.canvas.height = 0
      }
      if (this.$refs.cameraStream) {
        this.$refs.cameraStream.style.display = 'block'
      }
      this.invoice = null
      this.paid = false
    },
    uploaded(e) {
      const data = JSON.parse(e.xhr.response)
      this.invoice = data.payment_request
      this.onPaid(data.payment_hash)
    },
    onPaid(payment_hash) {
      const ws = new WebSocket(`${websocketUrl}/${payment_hash}`)
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

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
      message: '',
      webcamError: ''
    }
  },
  mounted() {
    if (this.$refs.cameraStream) {
      navigator.mediaDevices
        .getUserMedia({
          video: {
            FacingMode: 'user'
          },
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
    mmToPx(mm) {
      const dpi = 300
      return Math.floor((mm * dpi) / 25.4)
    },
    takePicture() {
      this.picture = true
      this.webcam = false
      this.$refs.cameraStream.style.display = 'none'
      const targetWidth = this.mmToPx(width)
      const targetHeight = this.mmToPx(height)
      this.$refs.canvas.width = targetWidth
      this.$refs.canvas.height = targetHeight
      const originalWidth = this.$refs.cameraStream.videoWidth
      const originalHeight = this.$refs.cameraStream.videoHeight
      const hRatio = targetWidth / originalWidth
      const vRatio = targetHeight / originalHeight
      const ratio = Math.min(hRatio, vRatio)
      const centerShift_x = (targetWidth - originalWidth * ratio) / 2
      const centerShift_y = (targetHeight - originalHeight * ratio) / 2
      const ctx = this.$refs.canvas.getContext('2d')
      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, targetWidth, targetHeight)
      ctx.drawImage(
        this.$refs.cameraStream,
        0,
        0,
        originalWidth,
        originalHeight,
        centerShift_x,
        centerShift_y,
        originalWidth * ratio,
        originalHeight * ratio
      )
    },
    uploadText() {
      if (this.message.length === 0) return
      const blob = new Blob([this.message], {type: 'plain/text'})
      const formData = new FormData()
      formData.append('file', blob, 'message.txt')
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
            message: 'Text uploaded successfully'
          })
        })
        .catch(LNbits.utils.notifyApiError)
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

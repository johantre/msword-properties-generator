    // ===============================================
    // Variable declarations
    // ===============================================

    // DOM references
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const cropBtn = document.getElementById('cropBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const openFormBtn = document.getElementById('openFormBtn');
    const status = document.getElementById('status');
    const copyLinkBtn = document.getElementById('copyLinkBtn');
    const linkDisplay = document.getElementById('linkDisplay');
    const brightnessSlider = document.getElementById("brightness");
    const contrastSlider = document.getElementById("contrast");
    const imagePreview = document.getElementById("preview");
    const cropperContainer = document.getElementById("cropperContainer");

    // Cropper and image state
    let cropper;
    let cropperState = null;
    let croppedBlob;
    let downloadURL;
    let resizeTimer;

    // ===============================================
    // Function declarations
    // ===============================================

    function updateImageFilters() {
      const brightness = brightnessSlider.value;
      const contrast = contrastSlider.value;
      cropperContainer.style.filter = `brightness(${brightness}) contrast(${contrast})`;
    }

    function updateButtonText() {
      const isMobile = window.matchMedia("(max-width: 768px)").matches;
      const uploadButton = document.querySelector('.file-upload-button');
      uploadButton.textContent = isMobile ? "Snap Signature" : "Choose Signature image";
    }

    function updateCropperScale() {
      if (!cropper) return;

      const container = document.getElementById('cropperContainer');
      const containerRect = container.getBoundingClientRect();
      const targetRatio = 945/535;

      let width = containerRect.width;
      let height = width / targetRatio;

      if (height > containerRect.height) {
          height = containerRect.height;
          width = height * targetRatio;
      }

      const left = (containerRect.width - width) / 2;
      const top = (containerRect.height - height) / 2;

      cropper.setCanvasData({
          left: left,
          top: top,
          width: width,
          height: height
      });

      cropper.setCropBoxData({
          left: left,
          top: top,
          width: width,
          height: height
      });
    }

    function resizeCanvasToWindow() {
      if (!cropper) return;

      const headerHeight = 100;
      const controlsHeight = 200;
      const availableHeight = window.innerHeight - headerHeight - controlsHeight;
      const availableWidth = window.innerWidth * 0.9;
      const container = document.getElementById('cropperContainer');

      const targetRatio = 945/535;
      let containerWidth = availableWidth;
      let containerHeight = containerWidth / targetRatio;

      if (containerHeight > availableHeight) {
          containerHeight = availableHeight;
          containerWidth = containerHeight * targetRatio;
      }

      container.style.width = containerWidth + 'px';
      container.style.height = containerHeight + 'px';

      if (cropper) {
          const canvasData = {
              left: 0,
              top: 0,
              width: containerWidth,
              height: containerHeight
          };
          console.log("canvasData before setCanvasData:", canvasData);
          cropper.setCanvasData(canvasData);

          const cropBoxData = cropper.getCropBoxData();
          if (cropBoxData) {
              const aspectRatio = 945/535;
              let newWidth = containerWidth * 0.9;
              let newHeight = newWidth / aspectRatio;

              if (newHeight > containerHeight * 0.9) {
                  newHeight = containerHeight * 0.9;
                  newWidth = newHeight * aspectRatio;
              }

              cropper.setCropBoxData({
                  left: (containerWidth - newWidth) / 2,
                  top: (containerHeight - newHeight) / 2,
                  width: newWidth,
                  height: newHeight
              });
          }
      }
    }

    // ===============================================
    // Event listeners / Initializations
    // ===============================================

    updateButtonText();

    document.getElementById('rotateLeft').addEventListener('click', function () {
      cropper.rotate(-90);
      updateCropperScale();
    });

    document.getElementById('rotateRight').addEventListener('click', function () {
      cropper.rotate(90);
      updateCropperScale();
    });

    brightnessSlider.addEventListener("input", updateImageFilters);

    contrastSlider.addEventListener("input", updateImageFilters);

    fileInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        document.querySelector('.cropper-and-controls').style.display = 'flex';
        document.getElementById('rotateButtons').style.display = 'flex';
        const reader = new FileReader();
        reader.onload = function(event) {
          preview.src = event.target.result;
          preview.style.display = 'block';

          preview.onload = function() {
            if (cropper) {
              cropper.destroy();
            }
            cropper = new Cropper(preview, {
                aspectRatio: 945/535,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
                background: true,
                guides: false
            });
          }
          uploadBtn.disabled = true;
          cropBtn.disabled = false;
          brightnessSlider.disabled = false;
          contrastSlider.disabled = false;

          cropBtn.style.display = 'inline';
          uploadBtn.style.display = 'inline';

          status.textContent = '';
          linkDisplay.textContent = '';
          openFormBtn.style.display = 'none';
          copyLinkBtn.style.display = 'none';

          brightnessSlider.value = 1;
          contrastSlider.value = 1;
          updateImageFilters();

          if (cropper) {
            cropper.destroy();
          }

          preview.style.display = 'block';
          preview.src = event.target.result;
          cropperContainer.classList.add('has-image');

          cropper = new Cropper(preview, {
            viewMode: 2,
            dragMode: 'move',
            aspectRatio: 945/535,
            autoCropArea: 1,
            restore: false,
            guides: false,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
            responsive: true,
            ready: function() {
              this.cropper.clear();
              resizeCanvasToWindow();
              updateCropperScale();
              setTimeout(updateCropperScale, 100);

              setTimeout(() => {
                const cropperBox = document.getElementById('cropperContainer').getBoundingClientRect();
                const imageData = this.cropper.getImageData();

                const scale = cropperBox.height / imageData.naturalHeight;

                const scaledHeight = cropperBox.height;
                const scaledWidth = imageData.naturalWidth * scale;

                this.cropper.setCanvasData({
                  left: (cropperBox.width - scaledWidth) / 2,
                  top: 0,
                  width: scaledWidth,
                  height: scaledHeight
                });

                const cropBoxWidth = Math.min(cropperBox.width * 0.9, scaledWidth);
                const cropBoxHeight = (cropBoxWidth * 535) / 945;

                this.cropper.setCropBoxData({
                  left: (cropperBox.width - cropBoxWidth) / 2,
                  top: (cropperBox.height - cropBoxHeight) / 3,
                  width: cropBoxWidth,
                  height: cropBoxHeight
                });

                this.cropper.crop();
                updateCropperScale();
              }, 100);
            },
            zoom: function(e) {
              if (e.detail.ratio < 0.5) {
                e.preventDefault();
              }
              if (e.detail.ratio > 3) {
                e.preventDefault();
              }
            }
          });
        };
        reader.readAsDataURL(file);
      }
    });

    cropperContainer.style.overflow = "visible";

    window.addEventListener('load', resizeCanvasToWindow);

    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
        if (cropper && preview.src) {
          cropper.destroy();
          cropper = new Cropper(preview, {
            aspectRatio: 945 / 535,
            viewMode: 1,
            autoCropArea: 1,
            guides: false,
            responsive: true,
            background: true,
          });
        }
        }, 200);
    });

    const containerStyle = `
    #cropperContainer {
        overflow: hidden;
        position: relative;
    }
    `;

    const styleSheet = document.createElement("style");
    styleSheet.innerText = containerStyle;
    document.head.appendChild(styleSheet);

    cropBtn.addEventListener('click', () => {
      const canvas = cropper.getCroppedCanvas();
      if (canvas.width < 10 || canvas.height < 10) {
        status.textContent = 'Please select a larger crop area.';
        return;
      }
      const brightness = parseFloat(document.getElementById('brightness').value);
      const contrast = parseFloat(document.getElementById('contrast').value);
      uploadBtn.disabled = false;

      const filteredCanvas = document.createElement('canvas');
      filteredCanvas.width = canvas.width;
      filteredCanvas.height = canvas.height;
      const ctx = filteredCanvas.getContext('2d');
      ctx.filter = `brightness(${brightness}) contrast(${contrast})`;
      ctx.drawImage(canvas, 0, 0);

      filteredCanvas.toBlob((blob) => {
        if (!blob) {
          status.textContent = 'Error while processing image.';
          return;
        }
        croppedBlob = blob;
        uploadBtn.style.display = 'inline';
        document.getElementById('filters').style.display = 'block';
        status.textContent = 'Ready to upload';
      }, 'image/png');
    });

    uploadBtn.addEventListener('click', () => {
      if (!croppedBlob) return;
      status.textContent = 'Uploading...';
      uploadBtn.disabled = true;
      cropBtn.disabled = true;
      if (cropper) {
        cropper.disable();
      }
      brightnessSlider.disabled = true;
      contrastSlider.disabled = true;

      const formData = new FormData();
      formData.append('files[]', croppedBlob, 'signature.png');

      fetch('https://msword-signature-proxy.johan-tre.workers.dev/', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) {
          uploadBtn.disabled = false;
          cropBtn.disabled = false;
          brightnessSlider.disabled = false;
          contrastSlider.disabled = false;
          if (cropper) {
            cropper.enable();
          }
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        downloadURL = data.files[0].url;
        linkDisplay.textContent = downloadURL;
        navigator.clipboard.writeText(downloadURL).then(() => {
          status.textContent = 'Upload Complete. Link copied ...';
          linkDisplay.innerHTML = `<a href="${downloadURL}" target="_blank">${downloadURL}</a>`;
          openFormBtn.style.display = 'inline';
          copyLinkBtn.style.display = 'inline';
          copyLinkBtn.disabled = false;
        });
      })
      .catch(error => {
        uploadBtn.disabled = false;
        cropBtn.disabled = false;
        if (cropper) {
          cropper.enable();
        }
        console.error('Upload error:', error);
        status.textContent = `Error while uploading: ${error.message}`;
      });
    });

    openFormBtn.addEventListener('click', () => {
      window.open('https://github.com/johantre/msword-properties-generator/actions/workflows/subscribe-or-update-provider.yml', '_blank');
    });

    copyLinkBtn.addEventListener('click', () => {
      if (!downloadURL) return;
      navigator.clipboard.writeText(downloadURL)
        .then(() => {
          status.textContent = 'Link copied to clipboard.';
        })
        .catch(err => {
          console.error('Clipboard error:', err);
          status.textContent = 'Failed to copy link.';
        });
    });

    document.querySelector('.file-upload-button').addEventListener('click', () => {
      document.getElementById('fileInput').click();
    });

// ===============================================
// Variable declarations
// ===============================================
// DOM references
let cropper = null;
let rotation = 0;
let originalWidth = 0;
let originalHeight = 0;
let currentWidth = 0;
let currentHeight = 0;

// Cropper and image state
const preview = document.getElementById('preview');
const fileInput = document.getElementById('fileInput');
const cropperAndControls = document.querySelector('.cropper-and-controls');
const rotateLeft = document.getElementById('rotateLeft');
const rotateRight = document.getElementById('rotateRight');
const rotateButtons = document.getElementById('rotateButtons');
const cropBtn = document.getElementById('cropBtn');
const uploadBtn = document.getElementById('uploadBtn');
const openFormBtn = document.getElementById('openFormBtn');
const status = document.getElementById('status');
const copyLinkBtn = document.getElementById('copyLinkBtn');
const linkDisplay = document.getElementById('linkDisplay');
const brightnessSlider = document.getElementById("brightness");
const contrastSlider = document.getElementById("contrast");


// ===============================================
// Function declarations
// ===============================================
function fitAndCenter() {
    if (!cropper) return;

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            const containerData = cropper.getContainerData();
            const canvasData = cropper.getCanvasData();

            if (!containerData || !canvasData) return;

            const scaleX = containerData.width / canvasData.width;
            const scaleY = containerData.height / canvasData.height;
            const scale = Math.min(scaleX, scaleY);

            const curScale = canvasData.width / canvasData.naturalWidth;
            cropper.zoomTo(curScale * scale);

            requestAnimationFrame(() => {
                const newContainerData = cropper.getContainerData();
                const newCanvasData = cropper.getCanvasData();

                const offsetX = (newContainerData.width - newCanvasData.width) / 2;
                const offsetY = (newContainerData.height - newCanvasData.height) / 2;

                cropper.moveTo(offsetX, offsetY);
            });
        });
    });
}

function rotateAndFit(degrees) {
  if (!cropper) return;

  rotation = (rotation + degrees) % 360;
  if (rotation < 0) rotation += 360;
  cropper.rotateTo(rotation);

  setTimeout(() => {
    centerCropBox(0.6);
  }, 70);
}

function resizeCropperContainer() {
    const cropperContainer = document.getElementById('cropperContainer');
    const controlsHeight = 400;
    const margin = 24;
    const availableHeight = window.innerHeight - controlsHeight - margin;
    cropperContainer.style.height = Math.max(availableHeight, 120) + 'px';

    setTimeout(() => {
        if (cropper) {
            requestAnimationFrame(() => {
                fitAndCenter();
            });
        }
    }, 30);
}

function centerCropBox(scale = 0.6) {
  if (!cropper) return;
  const canvasData = cropper.getCanvasData();

  const ratio = 945 / 535;

  let maxWidth = canvasData.width * scale;
  let maxHeight = canvasData.height * scale;
  let width = maxWidth;
  let height = width / ratio;
  if (height > maxHeight) {
    height = maxHeight;
    width = height * ratio;
  }

  const centerX = canvasData.left + canvasData.width / 2;
  const centerY = canvasData.top + canvasData.height / 2;
  const left = centerX - width / 2;
  const top = centerY - height / 2;
  cropper.setAspectRatio(ratio);
  cropper.setCropBoxData({ left, top, width, height });
}

function rotateAndCenter(degrees = 90, scale = 0.6) {
  if (!cropper) return;
  cropper.rotate(degrees);
  setTimeout(() => {
    centerCropBox(scale);
  }, 150);
}

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

// ===============================================
// Event listeners / Initializations
// ===============================================
updateButtonText();

window.addEventListener('DOMContentLoaded', resizeCropperContainer);

window.addEventListener('resize', resizeCropperContainer);

fileInput.addEventListener('change', function (e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (event) {
    preview.onload = function () {
      cropperAndControls.style.display = 'flex';
      preview.style.display = 'block';
      rotateButtons.style.display = 'flex';
      cropBtn.style.display = 'inline-block';
      uploadBtn.style.display = 'inline-block';

      brightnessSlider.disabled = false;
      contrastSlider.disabled = false;
      rotateLeft.disabled = false;
      rotateRight.disabled = false;
      cropBtn.disabled = false;

      originalWidth = preview.naturalWidth;
      originalHeight = preview.naturalHeight;
      currentWidth = originalWidth;
      currentHeight = originalHeight;
      rotation = 0;

      if (cropper) cropper.destroy();
      cropper = new Cropper(preview, {
        aspectRatio: 945 / 535,
        viewMode: 1,
        autoCropArea: 0.4,
        background: true,
        responsive: true,
        autoCrop: true,
        dragMode: 'move',
        movable: true,
        zoomable: true,
        ready: () => {
          fitAndCenter();
          centerCropBox();
        },
      });
      resizeCropperContainer();
    };
    preview.src = event.target.result;
  };
  reader.readAsDataURL(file);
});

brightnessSlider.addEventListener("input", updateImageFilters);

contrastSlider.addEventListener("input", updateImageFilters);

openFormBtn.addEventListener('click', () => {
  window.open('https://github.com/johantre/msword-properties-generator/actions/workflows/subscribe-or-update-provider.yml', '_blank');
});

rotateRight.addEventListener('click', function () {
  rotateAndFit(90);
  setTimeout(() => {
    fitAndCenter();
    setTimeout(() => {
      if (cropper) {
        centerCropBox();
      }
    }, 70);
  }, 80);
});

rotateLeft.addEventListener('click', function () {
  rotateAndFit(-90);
  setTimeout(() => {
    fitAndCenter();
    setTimeout(() => {
      if (cropper) {
        centerCropBox();
      }
    }, 70);
  }, 80);
});

uploadBtn.addEventListener('click', () => {
  if (!croppedBlob) return;
  status.textContent = 'Uploading...';
  brightnessSlider.disabled = true;
  contrastSlider.disabled = true;
  rotateLeft.disabled = true;
  rotateRight.disabled = true;
  uploadBtn.disabled = true;
  cropBtn.disabled = true;
  if (cropper) {
    cropper.disable();
  }

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
    status.textContent = 'Ready to upload';
  }, 'image/png');
});


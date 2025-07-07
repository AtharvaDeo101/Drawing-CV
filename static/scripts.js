class OpenCVWebcamCanvasApp {
  constructor() {
    this.webcamVideo = document.getElementById("webcamVideo");
    this.drawingCanvas = document.getElementById("drawingCanvas");
    this.startButton = document.getElementById("startWebcam");
    this.drawingCtx = this.drawingCanvas.getContext("2d");
    this.prevPoint = null;

    this.initializeCanvas();
    this.setupEventListeners();
  }

  initializeCanvas() {
    // Set canvas background to white
    this.drawingCtx.fillStyle = "white";
    this.drawingCtx.fillRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);

    // Set drawing properties
    this.drawingCtx.strokeStyle = "black"; // Matches backend drawColor (0, 0, 0)
    this.drawingCtx.lineWidth = 6; // Matches backend brushthick
    this.drawingCtx.lineCap = "round";
    this.drawingCtx.lineJoin = "round";
  }

  setupEventListeners() {
    // Start/stop webcam button
    this.startButton.addEventListener("click", () => {
      if (this.webcamVideo.src) {
        this.stopWebcam();
      } else {
        this.startWebcam();
      }
    });
  }

  startWebcam() {
    this.webcamVideo.src = "/video_feed"; // Start Flask video stream
    this.startButton.textContent = "Stop Webcam";
    this.startButton.disabled = true; // Disable until stream starts
    this.processStream();
  }

  stopWebcam() {
    this.webcamVideo.src = ""; // Stop stream
    this.startButton.textContent = "Start Webcam";
    this.startButton.disabled = false;
    this.drawingCtx.fillStyle = "white";
    this.drawingCtx.fillRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
    this.prevPoint = null;
  }

  processStream() {
    fetch(this.webcamVideo.src, { method: "GET" })
      .then(response => {
        const reader = response.body.getReader();
        let isFrame = true;

        const read = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              console.log("Stream ended");
              this.stopWebcam();
              return;
            }

            if (isFrame) {
              // Process video frame
              const blob = new Blob([value], { type: "image/jpeg" });
              this.webcamVideo.src = URL.createObjectURL(blob);
              isFrame = false;
            } else {
              // Process metadata (draw_data and canvas)
              const text = new TextDecoder().decode(value);
              try {
                const data = JSON.parse(text.split("\r\n")[0]);
                const drawData = data.draw_data;

                if (drawData.clear) {
                  this.drawingCtx.fillStyle = "white";
                  this.drawingCtx.fillRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
                  this.prevPoint = null;
                } else if (drawData.draw && drawData.x && drawData.y) {
                  const x = drawData.x * (this.drawingCanvas.width / 640); // Scale to canvas size
                  const y = drawData.y * (this.drawingCanvas.height / 480);
                  if (this.prevPoint) {
                    this.drawingCtx.beginPath();
                    this.drawingCtx.moveTo(this.prevPoint.x, this.prevPoint.y);
                    this.drawingCtx.lineTo(x, y);
                    this.drawingCtx.stroke();
                  }
                  this.prevPoint = { x, y };
                } else {
                  this.prevPoint = null;
                }

                // Update canvas with server canvas image
                const img = new Image();
                img.src = "data:image/jpeg;base64," + data.canvas;
                img.onload = () => {
                  this.drawingCtx.drawImage(img, 0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
                };
              } catch (e) {
                console.error("Error parsing JSON:", e);
              }
              isFrame = true;
            }
            read();
          }).catch(error => {
            console.error("Stream error:", error);
            this.stopWebcam();
          });
        };
        read();
      })
      .catch(error => {
        console.error("Fetch error:", error);
        this.startButton.disabled = false;
        this.startButton.textContent = "Start Webcam";
      });
  }

  // Optional: Add a method to clear the canvas manually (if you add a clear button)
  clearCanvas() {
    this.drawingCtx.fillStyle = "white";
    this.drawingCtx.fillRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
    this.prevPoint = null;
  }
}

// Initialize the app when the page loads
window.addEventListener("load", () => {
  new OpenCVWebcamCanvasApp();
});
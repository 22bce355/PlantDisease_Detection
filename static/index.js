document.addEventListener("DOMContentLoaded", function () {
    const openCameraButton = document.getElementById("openCamera");
    const captureButton = document.getElementById("capture");
    const uploadButton = document.getElementById("uploadImage");
    const video = document.getElementById("camera");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");

    let stream = null;

    openCameraButton.addEventListener("click", async () => {
        if (!stream) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                video.style.display = "block";
                captureButton.style.display = "block";
            } catch (err) {
                console.error("Error accessing camera:", err);
            }
        }
    });

    captureButton.addEventListener("click", () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        video.style.display = "none";
        captureButton.style.display = "none";
        uploadButton.style.display = "block";
    });

    uploadButton.addEventListener("click", () => {
        canvas.toBlob((blob) => {
            const formData = new FormData();
            formData.append("file", blob, "captured_image.jpg");

            fetch("/upload_camera", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        }, "image/jpeg");
    });
});

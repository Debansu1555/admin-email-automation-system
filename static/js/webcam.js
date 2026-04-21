const stream = await navigator.mediaDevices.getUserMedia({ video: true });
document.querySelector("video").srcObject = stream;
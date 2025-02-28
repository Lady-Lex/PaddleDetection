<template>
  <video id="video" width="300" height="300"
    poster="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic.51yuansu.com%2Fpic3%2Fcover%2F01%2F14%2F62%2F59043cebb703f_610.jpg&refer=http%3A%2F%2Fpic.51yuansu.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1637115934&t=cd4ebc01b4b11fb45ce65a3b2dc7e933"></video>
  <canvas id="canvas" width="300" height="300" hidden></canvas><br>
  <img id="processed_image" src="" alt="" />
</template>


<script setup>
import axios from 'axios';
import { ref } from 'vue';

axios.defaults.withCredentials = true; // 让 ajax 携带 cookie

import { getCurrentInstance, onMounted } from 'vue';

const { proxy } = getCurrentInstance()

var serverHost = ref('10.29.0.151')
var serverPort = ref(3200)

function clear() {
  axios.get('https://' + serverHost.value + ':' + serverPort.value, {
  })
    .then((res) => {
      console.log(res)
    }).catch((err) => {

    }).then(() => {

    })
}

onMounted(() => {
  clear()

  //视频窗口尺寸
  let size = 300;
  let video = document.getElementById('video');
  let canvas = document.getElementById('canvas');
  let context = canvas.getContext('2d');
  let processed_image = document.getElementById('processed_image');

  //用来匹配不同的浏览器
  function getUserMedia(constraints, success, error) {
    if (navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia(constraints).then(success).catch(error);
    } else if (navigator.webkitGetUserMedia) {
      navigator.webkitGetUserMedia(constraints, success, error);
    } else if (navigator.mozGetUserMedia) {
      navigator.mozGetUserMedia(constraints, success, error);
    } else if (navigator.getUserMedia) {
      navigator.getUserMedia(constraints, success, error)
    }
  }

  //成功回调
  function success(stream) {
    video.srcObject = stream
    video.play()
  }
  //失败回调
  function error(error) {
    console.log("访问用户媒体失败");
  }

  if (navigator.mediaDevices.getUserMedia || navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia) {
    getUserMedia({
      video:
      {
        width: size,
        height: size,
        facingMode: "environment",
        // facingMode: { exact: "environment" },
      }
    }, success, error)
  } else {
    alert("不支持");
  }

  setInterval(() => {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    axios.post('http://' + serverHost.value + ':' + serverPort.value + "/upload", {
      data: canvas.toDataURL("image/png")
    })
      .then((res) => {
        console.log(res)
        processed_image.setAttribute('src', "data:image/png;base64," + res.data.processed_image_base64)
      }).catch((err) => {

      }).then(() => {

      })
  }, 50);
})


</script>





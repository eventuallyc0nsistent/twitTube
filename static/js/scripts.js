(function(exports) {

exports.URL = exports.URL || exports.webkitURL;

exports.requestAnimationFrame = exports.requestAnimationFrame ||
    exports.webkitRequestAnimationFrame || exports.mozRequestAnimationFrame ||
    exports.msRequestAnimationFrame || exports.oRequestAnimationFrame;

exports.cancelAnimationFrame = exports.cancelAnimationFrame ||
    exports.webkitCancelAnimationFrame || exports.mozCancelAnimationFrame ||
    exports.msCancelAnimationFrame || exports.oCancelAnimationFrame;

navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia || navigator.mozGetUserMedia ||
    navigator.msGetUserMedia;

var ORIGINAL_DOC_TITLE = document.title;
var video = $('video#video-recorder');
var canvas = document.createElement('canvas'); // offscreen canvas.
var rafId = null;
var startTime = null;
var endTime = null;
var frames = [];
var localMediaStream,recorder;
var blob = null;

function $(selector) {
  return document.querySelector(selector) || null;
}

function toggleActivateRecordButton() {
  var b = $('#record-me');
  b.textContent = b.disabled ? 'Record' : 'Recording...';
  b.classList.toggle('recording');
  b.disabled = !b.disabled;
}

function turnOnCamera(e) {
  e.target.disabled = true;
  $('#record-me').disabled = false;

  video.controls = false;

  var finishVideoSetup_ = function() {
    
    setTimeout(function() {
      video.width = 320;//video.clientWidth;
      video.height = 240;// video.clientHeight;
      
      canvas.width = video.width;
      canvas.height = video.height;
    }, 1000);
  };

  navigator.getUserMedia({video: true, audio: false}, function(stream) {
    video.src = window.URL.createObjectURL(stream);
    finishVideoSetup_();
  }, function(e) {
    alert('You haven\'t given permission to record video or your browser needs to be upgraded.');

    video.src = 'Chrome_ImF.mp4';
    finishVideoSetup_();
  });
};

function record() {
  var elapsedTime = $('#elasped-time');
  var ctx = canvas.getContext('2d');
  var CANVAS_HEIGHT = canvas.height;
  var CANVAS_WIDTH = canvas.width;

  frames = []; // clear existing frames;
  startTime = Date.now();

  toggleActivateRecordButton();
  $('#stop-me').disabled = false;

  function drawVideoFrame_(time) {
    rafId = requestAnimationFrame(drawVideoFrame_);

    ctx.drawImage(video, 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    document.title = 'Recording...' + Math.round((Date.now() - startTime) / 1000) + 's';

    var url = canvas.toDataURL('image/webp', 1); // image/jpeg is way faster :(
    frames.push(url);
  };

  rafId = requestAnimationFrame(drawVideoFrame_);
};

function stop() {

  document.getElementById("progressbar").style.display = 'block';

  cancelAnimationFrame(rafId);
  endTime = Date.now();
  $('#stop-me').disabled = true;
  document.title = ORIGINAL_DOC_TITLE;

  toggleActivateRecordButton();

  console.log('frames captured: ' + frames.length + ' => ' +
              ((endTime - startTime) / 1000) + 's video');

  embedVideoPreview();


};

function embedVideoPreview(opt_url) {
  var url = opt_url || null;
  var video = $('#video-preview video') || null;
  var downloadLink = $('#video-preview a[download]') || null;

  if (!video) {
    video = document.createElement('video');
    video.autoplay = true;
    video.controls = true;
    video.loop = true;
    video.style.width = canvas.width + 'px';
    video.style.height = canvas.height + 'px';
    $('#video-preview').appendChild(video);
    
    downloadLink = document.createElement('a');
    downloadLink.download = 'capture.webm';
    downloadLink.textContent = '[ download video ]';
    downloadLink.title = 'Download your .webm video';
    var p = document.createElement('p');
    p.appendChild(downloadLink);

    $('#video-preview').appendChild(p);

  } else {
    window.URL.revokeObjectURL(video.src);
  }

  if (!url) {
    var webmBlob = Whammy.fromImageArray(frames, 1000 / 60);
    url = window.URL.createObjectURL(webmBlob);
  }

  video.src = url;
  downloadLink.href = url;
  saveVideoURL = url;


  var xhr = new XMLHttpRequest();

  // get the blob file
  xhr.open('GET',saveVideoURL,true);
  xhr.responseType = 'blob';
  xhr.onload =function(e){
  if(this.status == 200){
		blob = this.response;
    saveBlob(blob);
	}
	else {
		console.log(e);
	 }
  }
  xhr.send();

}

function updateProgress(e) 
{
   var progressBar = document.querySelector('progress');

   if (e.lengthComputable) {
      progressBar.value = (e.loaded / e.total) * 100;
      progressBar.textContent = progressBar.value; // Fallback for unsupported browsers.

      if(progressBar.value == 100) {
        document.getElementById("progressbar").style.display = 'block';
      }
    }


}   

function saveBlob(blob){

  if(window.location.pathname == '/reply'){
    // get the id of the reply
    var post_id = window.location.search.split('&')[0].split("=")[1];
    var sender_id = window.location.search.split('&')[1].split("=")[1];
    // console.log(post_id)
    // console.log(sender_id)
    var video_path = '/upload-video?post-id='+post_id+"&sender="+sender_id
  } else {
    var video_path = '/upload-video'
  }

  // var title = document.getElementById('video-title').value;
  // console.log("Title of video:"+title);

  // upload video from XHR
  var xhr = new XMLHttpRequest();

  xhr.onload = function(e){
    if(this.status = 200){
      // loaded path
      console.log("Size received:"+blob.size)
      console.log("Type of blob:"+blob.type)
    }
    else {
      alert("Sorry! Try again. We were not able to record your video.")
    }
  }

  xhr.upload.onprogress = function(e) {
    updateProgress(e);
  }

  // Send video to path
  xhr.open('POST',video_path,true);
  xhr.setRequestHeader("Content-type",blob.type);
  xhr.send(blob);

}

function initEvents() {
  $('#camera-me').addEventListener('click', turnOnCamera);
  $('#record-me').addEventListener('click', record);
  $('#stop-me').addEventListener('click', stop);

}

initEvents();

exports.$ = $;

})(window);

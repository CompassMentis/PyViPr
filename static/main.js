function showRecordingsList() {
  $.ajax({
    url: "/api/audio/list_recordings/",
    method: "POST",
    data: { part_name:part_name, step_line_number:step_line_number },
    success: function(data, textStatus, jqXHR){
      $("#audio-recordings-list").html(data);
      setButtons();
    }
  });
}

function startRecording() {
  recording = true;
  $("#start-recording-button").hide();
  $("#stop-recording-button").show();
  data = {
        part_name:part_name,
        step_line_number:step_line_number
      };
  $.post("/api/audio/start_recording", data);
}

function stopRecording() {
  recording = true;
  $("#start-recording-button").show();
  $("#stop-recording-button").hide();
  $.ajax({
    url: "/api/audio/stop_recording",
    method: "GET",
    success: function(data, textStatus, jqXHR) {
        showRecordingsList();
    }
  });
}

function startPlay() {
  $.post(
    "/api/audio/start_play",
    { part_name:part_name, file_name: $(this).data("file_name") }
  );
}

function changeRecordingStatus(file_name, new_status){
  $.ajax({
    url: "/api/audio/change_status",
    method: "POST",
    data: { part_name: part_name, file_name: file_name, new_status: new_status },
    success: function(data, textStatus, jqXHR) {
        showRecordingsList();
    }
  });
}

function stopPlay() {
  $.get("/api/audio/stop_play");
}

function tbdRecording() {
  changeRecordingStatus($(this).data("file_name"), 'tbd');
}

function yesRecording() {
  changeRecordingStatus($(this).data("file_name"), 'yes');
}

function noRecording() {
  changeRecordingStatus($(this).data("file_name"), 'no');
}

function setButtons() {
    $("#start-recording-button").on("click", startRecording);
    $("#stop-recording-button").on("click", stopRecording);
    $("#stop-recording-button").hide();
    $(".audio-recording-start-play-button").on("click", startPlay);
    $(".audio-recording-stop-play-button").on("click", stopPlay);
    $(".audio-recording-tbd-button").on("click", tbdRecording);
    $(".audio-recording-yes-button").on("click", yesRecording);
    $(".audio-recording-no-button").on("click", noRecording);
}

$(
  function() {
    recording = false;
    showRecordingsList();
  }
);

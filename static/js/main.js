function parse_duration(dur_string) {
  let rv = 0;
  let chunks = dur_string.split(":").map(chunk => parseFloat(chunk).toFixed());
  rv += chunks[2] * 1000;
  rv += chunks[1] * 60 * 1000;
  rv += chunks[0] * 60 * 60 * 1000;
  return rv;
}

function duration_to_str(dur) {
  let minutes = Math.floor(dur / 60000).toString().padStart(2, "0");
  let seconds = (Math.floor(dur / 1000) % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function setup_audio() {
  let ticking_audio = new Audio("/static/sounds/ticking2.wav");
  let ding_audio = new Audio("/static/sounds/ding.wav");
  ticking_audio.loop = true;
  const active_sessions_exist = sessions.some(
    (s) => s.fields.status == "ACTIVE"
  );
  if (active_sessions_exist) {
    ticking_audio.play();
  }

  let toggle_elm = document.querySelector("#toggle-audio");
  toggle_elm.addEventListener('click', e => {
    if (!ticking_audio.paused)
      ticking_audio.pause();
    else 
      ticking_audio.play();
  });
  return [ticking_audio, ding_audio];
}

function main(e) {
  let [ticking_audio, ding_audio] = setup_audio();

  for (let session of sessions) {
    let timer = document.querySelector(`#session-${session.pk}>.timer`);
    if (session.fields.status == "ACTIVE") {
      let start_time = new Date(session.fields.start);
      let paused_duration = parse_duration(
        session.fields.paused_duration || "0:0:0"
      );
      let target_duration = parse_duration(
        session.fields.target_duration ||
          alert("couldn't parse target duration")
      );
      let active_duration = parse_duration(
        session.fields.target_duration ||
          alert("couldn't parse active duration")
      );

      if (active_duration > target_duration)
        return;

      let interval_id = setInterval(() => {
        let now = Date.now();
        let passed_duration = now - start_time - paused_duration;
        if (passed_duration < target_duration) {
          timer.textContent = ` ${duration_to_str(passed_duration)}`;
        } else {
          timer.textContent = `Finished`;
          ticking_audio.pause();
          ding_audio.play();
          clearInterval(interval_id);
        }
      }, 500);
    }
  }
}

document.addEventListener("DOMContentLoaded", main);
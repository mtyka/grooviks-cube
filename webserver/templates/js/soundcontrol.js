// ####################################################################
// ######################## SoundManager2 #############################
// ####################################################################

var masterVolume = 100;

soundManager.url = 'static';
//soundManager.preferFlash = false;
soundManager.useHTML5Audio = false;
soundManager.flashVersion = 9;
soundManager.useFastPolling = true;
soundManager.useHighPerformance = true;
soundManager.onload = function(){
  soundManager.createSound({ id: 'column1_1', url: '/static/synth_8bit_low_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column1_2', url: '/static/synth_8bit_med_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column1_3', url: '/static/synth_8bit_high_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column2_1', url: '/static/synth_tal_low_002.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column2_2', url: '/static/synth_tal_med_002.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column2_3', url: '/static/synth_tal_high_002.mp3', autoLoad: true });

  soundManager.createSound({ id: 'column3_1', url: '/static/vocoder_low_001.mp3', autoLoad: true }); 
  soundManager.createSound({ id: 'column3_2', url: '/static/vocoder_med_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'column3_3', url: '/static/vocoder_high_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'gear1', url: '/static/gear_001.mp3', autoLoad: true });
  soundManager.createSound({ id: 'gear2', url: '/static/gear_002.mp3', autoLoad: true });
  soundManager.createSound({ id: 'gear3', url: '/static/gear_003.mp3', autoLoad: true });
  soundManager.createSound({ id: 'victory1', url: '/static/mario1.mp3', autoLoad: true });

  soundManager.createSound({ id: '1', url: '/static/a_flat_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '2', url: '/static/a_flat_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '3', url: '/static/a_flat_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '4', url: '/static/a_flat_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '5', url: '/static/a_flat_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '6', url: '/static/a_flat_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '7', url: '/static/a_flat_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '8', url: '/static/a_flat_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '9', url: '/static/a_flat_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '10', url: '/static/a_major_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '11', url: '/static/a_major_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '12', url: '/static/a_major_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '13', url: '/static/a_major_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '14', url: '/static/a_major_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '15', url: '/static/a_major_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '16', url: '/static/a_major_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '17', url: '/static/a_major_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '18', url: '/static/a_major_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '19', url: '/static/b_major_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '20', url: '/static/b_major_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '21', url: '/static/b_major_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '22', url: '/static/b_major_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '23', url: '/static/b_major_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '24', url: '/static/b_major_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '25', url: '/static/b_major_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '26', url: '/static/b_major_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '27', url: '/static/b_major_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '28', url: '/static/d_flat_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '29', url: '/static/d_flat_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '30', url: '/static/d_flat_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '31', url: '/static/d_flat_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '32', url: '/static/d_flat_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '33', url: '/static/d_flat_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '34', url: '/static/d_flat_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '35', url: '/static/d_flat_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '36', url: '/static/d_flat_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '37', url: '/static/e_major_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '38', url: '/static/e_major_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '39', url: '/static/e_major_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '40', url: '/static/e_major_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '41', url: '/static/e_major_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '42', url: '/static/e_major_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '43', url: '/static/e_major_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '44', url: '/static/e_major_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '45', url: '/static/e_major_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '46', url: '/static/f_sharp_1_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '47', url: '/static/f_sharp_2_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '48', url: '/static/f_sharp_3_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '49', url: '/static/f_sharp_4_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '50', url: '/static/f_sharp_5_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '51', url: '/static/f_sharp_6_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '52', url: '/static/f_sharp_7_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '53', url: '/static/f_sharp_8_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '54', url: '/static/f_sharp_9_01.mp3', autoLoad: true });
  soundManager.createSound({ id: '55', url: '/static/d_flat_10_01.mp3', autoLoad: true });
};

function playFaceClickSound(frame){
	var playerNumber = Math.floor(frame.payload[1]/ 3) + 1;
	var columnNumber = (frame.payload[1] % 3) + 1;
  console.log(frame.payload);
  var sound_id = '' + frame.payload[0] + '';
  console.log(sound_id);
  var faceSound = soundManager.getSoundById(sound_id);
	
  faceSound.setVolume(masterVolume);
	faceSound.play();
}

function playRotationSound(rotationStep){
  if(rotationStep ){
    var gearSound = soundManager.getSoundById('gear' + rotationStep );
    gearSound.setVolume(masterVolume);
    gearSound.play();
  }
}

function playSound( soundid, stopall ){
  var the_sound = soundManager.getSoundById(soundid);
  if(stopall) soundManager.stopAll();
  the_sound.play();
}

function setMasterVolumeLevel(volumeLevel){
	masterVolume  = volumeLevel;
}

// This is a placeholder for a function that can handle pongs
pong_handler = null;

ping_handler = function(){
  HookboxConnection.hookbox_conn.publish("volumeControl", ["pong", position, masterVolume] );
}

function handle_vol(payload){
    if(payload[0] == "ping") {
        console.log("Volume ping");
        // ping handler is defined only by admin interface. Player mode does not respond or act on pongs
        if( ping_handler ) ping_handler();
    } else if( payload[0] == "pong" ){
        console.log("Volume pong");
        // pong handler is defined only by admin interface. Player mode does not respond or act on pongs
        if( pong_handler ) pong_handler( payload[1], payload[2]);
    } else if (payload[0] == "update") {
        console.log("Volume update");
        setMasterVolumeLevel(payload[parseInt(position)+1]);
    }
}



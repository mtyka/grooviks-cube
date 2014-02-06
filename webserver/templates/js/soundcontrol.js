// ####################################################################
// ######################## SoundManager2 #############################
// ####################################################################

var masterVolume = 100;
//DQ3LWSmRF3Xo7eimGDymTDD8t7VjfsEMwj
soundManager.url = 'static';
//soundManager.preferFlash = false;
soundManager.useHTML5Audio = false;
soundManager.flashVersion = 9;
soundManager.useFastPolling = true;
soundManager.useHighPerformance = true;
soundManager.onload = function(){
    soundManager.createSound({
        id: 'column1_1',
        url: '/static/synth_8bit_low_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column1_2',
        url: '/static/synth_8bit_med_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column1_3',
        url: '/static/synth_8bit_high_001.mp3',
        autoLoad: true
    });

     soundManager.createSound({
        id: 'column2_1',
        url: '/static/synth_tal_low_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column2_2',
        url: '/static/synth_tal_med_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column2_3',
        url: '/static/synth_tal_high_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column3_1',
        url: '/static/vocoder_low_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column3_2',
        url: '/static/vocoder_med_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column3_3',
        url: '/static/vocoder_high_001.mp3',
        autoLoad: true
    });
    soundManager.createSound({
        id: 'gear1',
        url: '/static/gear_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'gear2',
        url: '/static/gear_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'gear3',
        url: '/static/gear_003.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'victory1',
        url: '/static/mario1.mp3',
        autoLoad: true
    });
};

function playFaceClickSound(frame){
	var playerNumber = Math.floor(frame.payload[1]/ 3) + 1;
	var columnNumber = (frame.payload[1] % 3) + 1;
  var faceSound = soundManager.getSoundById('column'+ playerNumber  + '_' + columnNumber);
	faceSound.setVolume(masterVolume);
	soundManager.stopAll();
	faceSound.play();
}

function playRotationSound(rotationStep){
  console.log(rotationStep);
  if(rotationStep ){
    var gearSound = soundManager.getSoundById('gear' + rotationStep );
    gearSound.setVolume(masterVolume);
    //soundManager.stopAll();
    gearSound.play();
  }
}

function playSound( soundid, stopall ){
  var the_sound = soundManager.getSoundById(soundid)
  if(stopall) soundManager.stopAll();
  the_sound.play()
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
        console.log("Volume ping")
        // ping handler is defined only by admin interface. Player mode does not respond or act on pongs
        if( ping_handler ) ping_handler();
    } else if( payload[0] == "pong" ){
        console.log("Volume pong")
        // pong handler is defined only by admin interface. Player mode does not respond or act on pongs
        if( pong_handler ) pong_handler( payload[1], payload[2]);
    } else if (payload[0] == "update") {
        console.log("Volume update")
        setMasterVolumeLevel(payload[parseInt(position)+1]);
    }
}



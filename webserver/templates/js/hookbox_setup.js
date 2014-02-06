// ####################################################################
// #################### Communications Setup ##########################
// ####################################################################

var HookboxConnection = (function(){
	// public interface
	var my = {}
	my.hookbox_conn = null;

	// private vars:

	var is_hookbox_loaded = false;
	var subscription = null;

	// This code loads the hookbox.js from the current host but changing the port to 2974.
	var server = location.protocol + '//' + location.hostname + ':2974';

	// Dynamically inserts the code to load the script into the page.

	my.init = function(sScriptSrc, success_func ) {
		var headelem = document.getElementsByTagName('head')[0];
		var oScript = document.createElement('script');
		oScript.type = 'text/javascript';
		oScript.src = server + sScriptSrc;
		oScript.onload = function() {
			console.log("HOOKBOX LOADED!");
			is_hookbox_loaded = true;
			establish_hookbox_connections();
			if( success_func ) success_func();
		}
		oScript.onerror = function() {
			alert("Could not load library from hookbox server.");
		}
		headelem.appendChild(oScript);
	}

	function decompress_rgbfloat(rgb) {
		var output = [];
		output = rgb.split(" ");
		var rgb_floats = [ parseFloat(output[2]), parseFloat(output[1]), parseFloat(output[0])] ;
		return rgb_floats;
	}

	function establish_hookbox_connections() {
		if( !is_hookbox_loaded ) {
				alert("Failed to connect to hookbox server.");
		}

		// create a connection object and setup the basic event callbacks.
		my.hookbox_conn = hookbox.connect(server);
		//my.hookbox_conn.onOpen = function() { alert("connection established!"); };
		my.hookbox_conn.onError = function(err) { alert("Failed to connect to hookbox server: " + err.msg); };

		subscription = null;
		my.hookbox_conn.onSubscribed = function(channelName, _subscription) {
			try{
				if( channelName == 'iframe' ) {
					subscription = _subscription;
					subscription.onPublish = function(frame) {
						CubeControl.update_cube_state_from_datagram( frame.payload );
					};
				}
				if( channelName == 'faceclick' ) {
					faceclick_subscription = _subscription;
					faceclick_subscription.onPublish = function(frame) {
						playFaceClickSound(frame);
						console.log('Heard about click on face ' + frame.payload);
					};
				}

				if( channelName == 'colorcalibrx') {
					calib_subscription = _subscription;
					calib_subscription.onPublish = function(frame) {
						console.log('Heard calibration message');
						console.log(frame.payload);
						var rgb_floats = decompress_rgbfloat(frame.payload);

						changeSlider ( rgb_floats );
						console.log('done with calibration message');
					};
				}
				if( channelName == 'movesfromsolved' ) {
					movesfromsolved_subscription = _subscription;
					movesfromsolved_subscription.onPublish = function(frame) {
						return;
						//console.log('moves_from_solved has announced answer' + frame.payload);
						//moves_from_solved = frame.payload;
						// start inactivity counter which will trigger the message to appear
						//next_flash_moves_display = setTimeout("flash_moves_display()", 5000 );
					};
				}
				if( channelName == 'gameState' ) {
					gamestate_subscription = _subscription;
					gamestate_subscription.onPublish = function(frame) {
						on_game_state_change(frame.payload["gamestate"], frame.payload["active_position"], frame.payload["clientstate"]);
					};
				}
				if( channelName == 'rotationStep' ) {
					rotation_subscription = _subscription;
					rotation_subscription.onPublish = function(frame) {
						playRotationSound(frame.payload);
					};
				}
				if( channelName == 'volumeControl' ) {
					vol_subscription = _subscription;
					vol_subscription.onPublish = function(frame) {
						handle_vol(frame.payload);
					};
				}
				if( channelName == 'playsound' ){
					vol_subscription = _subscription;
					vol_subscription.onPublish = function(frame) {
						console.log(frame);
						playSound(frame.payload["soundid"], false);
					};
				}
				if( channelName == 'turns' ){
					turn_subscription = _subscription;
					turn_subscription.onPublish = function(frame) {
						global.currentTurn = frame.payload["turn"];
						global.activePlayers = [];

						var tmpActive = frame.payload["active"].replace(/(\[|\])/g, "").split(",").slice(0);

						for (var i=0; i < tmpActive.length; i++){
							if (tmpActive[0] == "")
								global.activePlayers = [];
							else
								global.activePlayers.push(parseInt(tmpActive[i]));
						}

						global.turnCheck();

						CubeControl.update_view();

						console.log("active players: " + global.activePlayers);
						console.log("current turn: " + global.currentTurn);
					}
				}
				if( channelName == 'settings' ){
					settings_subscription = _subscription;
					settings_subscription.onPublish = function(frame) {
						//console.log("Settings recieved");
						var setVal = function(id, f){
							$("#"+id).val(parseInt(f[id]));
						}

						console.log("Frame: ",frame);
						if (CubeControl.admin_mode){
							setVal("mp-turn-duration", frame.payload);
							setVal("mp-timeout-limit", frame.payload);
							setVal("sp-session-duration", frame.payload);
							setVal("mp-session-duration", frame.payload);
							setVal("menu-timeout", frame.payload);
						}
						else {
							timeout.mp_turn_duration = parseInt(frame.payload["mp-turn-duration"]);
							timeout.mp_timeout_limit = parseInt(frame.payload["mp-timeout-limit"]);
							timeout.sp_session_duration = parseInt(frame.payload["sp-session-duration"]);
							timeout.mp_session_duration = parseInt(frame.payload["mp-session-duration"]);
							timeout.menu_timeout = parseInt(frame.payload["menu-timeout"]);
						}
					};
				}
				if( channelName == 'vote' ){
					vote_subscription = _subscription;
					vote_subscription.onPublish = function(frame) {
						//console.log(frame);
						if (typeof(frame.payload["vote-for"]) != 'undefined' &&
								frame.payload["vote-for"] != position &&
			 					global.activePlayers.indexOf(parseInt(position)) >= 0){
							console.log("vote to add player " + frame.payload["vote-for"] + " to game");
							$("#player-add").html(frame.payload["vote-for"]);
							goto_vote_screen();
						}
						else if (typeof(frame.payload["vote-result"]) != 'undefined'){
							var res = frame.payload["vote-result"];
							var pos = frame.payload["position"];
							console.log("vote result: " + res + " for position " + pos);
							if (res == 1){ //vote success, alert in game clients,
								if (pos == position){
									clear_screen();
								}
								else if (global.activePlayers.indexOf(parseInt(position)) >= 0){
									goto_alert_screen("Multiplayer","Player "+pos+" has joined the Game!", 1500);
								}
							}
							else{ //vote fail, alert joiner
								if (pos == position){
									console.log("vote fail");
									goto_queued_screen();
								}
							}
						}
					};
				}
				if( channelName == 'timeout' ){
					timeout_subscription = _subscription;
					timeout_subscription.onPublish = function(frame) {
						//console.log("timeout frame: ", frame);
						timeout.set_game_time(frame.payload["set"]);
					};
				}
				if( channelName == 'difficulty' ){
					diff_subscription = _subscription;
					diff_subscription.onPublish = function(frame) {
						console.log("diff frame: ", frame);
						var diff = frame.payload["set"];

						global.difficulty = diff;
						diff = global.parseDifficulty();

						$("#difficulty").html(diff);
					};
				}
			}
			catch(e){
				console.log(e)
			}
		};

		// Subscribe to just the channels we'll need
		if (document.location.pathname == "/admin_cube"){
			console.log("----- IS ADMIN -----");
			my.hookbox_conn.subscribe("iframe");
			my.hookbox_conn.subscribe("faceclick");
			my.hookbox_conn.subscribe("gamemode");
			my.hookbox_conn.subscribe("gameState");
			my.hookbox_conn.subscribe("rotationStep");
			my.hookbox_conn.subscribe("volumeControl");
			my.hookbox_conn.subscribe("cubemode");
			my.hookbox_conn.subscribe("colorcalib");
			my.hookbox_conn.subscribe("colorcalibrx");
			my.hookbox_conn.subscribe("playsound");
			my.hookbox_conn.subscribe("settings");
		}
		else{
			console.log("----- IS MULTIMODE -----");
			my.hookbox_conn.subscribe("iframe");
			my.hookbox_conn.subscribe("faceclick");
			my.hookbox_conn.subscribe("gamemode");
			my.hookbox_conn.subscribe("gameState");
			my.hookbox_conn.subscribe("rotationStep");
			my.hookbox_conn.subscribe("volumeControl");
			my.hookbox_conn.subscribe("cubemode");
			my.hookbox_conn.subscribe("playsound");
			my.hookbox_conn.subscribe("clientcommand");
			my.hookbox_conn.subscribe("turns");
			my.hookbox_conn.subscribe("settings");
			my.hookbox_conn.subscribe("vote");
			my.hookbox_conn.subscribe("timeout");
			my.hookbox_conn.subscribe("difficulty");
		}
	}

	// return public interface
	return my;
}())



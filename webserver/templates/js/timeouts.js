// GAME TIMOUT COUNTER & LOGIC

var timeout = (function($){
	var self = this;

	var my = {};

	my.mp_timeout_limit = 2;
	my.mp_turn_duration	= 32;
	my.sp_session_duration = 321;
	my.mp_session_duration = 321;
	my.menu_timeout = 10;			//unimplemented

	var turn_timeleft = -1;
	var timeout_count =  0;
	var game_timeleft = -1;

	var gTimer = null;
	var tTimer = null;

	my.getTimeleft = function(){
		return [turn_timeleft, timeout_count, game_timeleft];
	}

//------ SYNC GAME TIMER -------
	my.set_game_time = function(actual){
		game_timeleft = actual;
	}

	my.get_real_game_timeleft = function(){
		return normalizeTime(game_timeleft);
	}

	my.get_game_time = function(){
		HookboxConnection.hookbox_conn.publish('timeout', 'get');
	}

//------ START TIMERS -------
	my.start_game_timeout = function(){
		if (client_state = "MULTIPLE")
			game_timeleft = my.mp_session_duration;
		else
			game_timeleft = my.sp_session_duration;

		if (!gTimer)
			gTimer = setInterval("self.update_game_timeout()", 1000);
		else{
			clearInterval(gTimer);
			gTimer = setInterval("self.update_game_timeout()", 1000);
		}

		my.get_game_time();
		$("#game_timeout").css("display", "inline");
	}

	my.start_turn_timeout = function(){
		if (global.currentTurn != position ||
			global.activePlayers.length <= 1 ||
			tTimer != null){
			return;
		}

		turn_timeleft = my.mp_turn_duration;

		if (!tTimer)
			tTimer = setInterval("self.update_turn_timeout()", 1000);
		else{
			clearInterval(tTimer);
			tTimer = setInterval("self.update_turn_timeout()", 1000);
		}

		$("#turn_timeout").css("display", "inline");
	}


//------ STOP TIMERS -------
	my.stop_game_timer = function(){
		game_timeleft = -1;
		clearInterval(gTimer);

		$("#game_timeout").css("display", "none");
	}

	my.stop_turn_timer = function(){
		turn_timeleft = -1;
		clearInterval(tTimer);

		$("#turn_timeout").css("display", "none");
	}

//------ RESET TIMERS -------
	my.reset_game_timeout = function(){
		if (client_state = "MULTIPLE")
			game_timeleft = my.mp_session_duration;
		else
			game_timeleft = my.sp_session_duration;
	}

	my.reset_turn_timeout = function(){
		turn_timeleft = my.mp_turn_duration;
	}

//------ UPDATE TIMERS -------
	self.update_game_timeout = function(){

		if (game_timeleft <= 0){
			clicked_quit();

			my.stop_game_timer();
			return;
		}

		game_timeleft -= 1;
		//console.log("timeleft: ", game_timeleft);
		$("#game_timeout").html("Session time remaining " + normalizeTime(game_timeleft));
	}

	self.update_turn_timeout = function(){
		if (global.currentTurn != position ||
			global.activePlayers.length <= 1){
			my.stop_turn_timer();
			return;
		}
		else if (turn_timeleft <= 0){
			timeout_count += 1;
			if (timeout_count == my.mp_timeout_limit){
				clicked_quit();
				goto_alert_screen("Timeout!", "", 3500);

				my.stop_turn_timer()
				return;
			}
			else{
				HookboxConnection.hookbox_conn.publish('faceclick', [-1, -1] );
				goto_alert_screen("Timeout!", "You have not made a move in time. Your turn has gone to another player.", 3500);

				my.stop_turn_timer();
				return;
			}
		}

		turn_timeleft -= 1;

		$("#turn_timeout").html("Time remaining for your turn " + normalizeTime(turn_timeleft));
	}

	my.update_game_timeout = self.update_game_timeout;
	my.update_turn_timeout = self.update_turn_timeout;

	function normalizeTime(t){
		return Math.floor(t/60).toString() + ":" + (t%60 < 10 ? ("0" + t%60).toString() : (t%60).toString());
	}

	return my;
}(jQuery))

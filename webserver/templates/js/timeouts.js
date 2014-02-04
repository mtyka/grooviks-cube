// GAME TIMOUT COUNTER & LOGIC

var timeout = (function($){
	var self = this;

	var my = {};

	my.mp_timeout_limit = 2;
	my.mp_turn_duration	= 30;
	my.sp_session_duration = 240;
	my.mp_session_duration = 240;
	my.menu_timeout = 10;

	var turn_timeleft = -1;
	var timeout_count =  0;
	var game_timeleft = -1;

	my.getTimeleft = function(){
		return [turn_timeleft, timeout_count, game_timeleft];
	}

	my.clear_game_timeout = function(){
		console.log( "Clear game timeout..." );
		game_timeleft = turn_timeleft = -1;
		$("#game_timeout").css("display", "none" );
	}

	my.clear_turn_timeout = function (){
		console.log( "Clear turn timeout..." );
		turn_timeleft = -1;
	}

	my.start_timeout = function(){
		if (client_state == "MULT"){
			game_timeleft = my.mp_session_duration;

			if (global.currentTurn == position)
				turn_timeleft = my.mp_turn_duration;

			timeout_count = 0;
			console.log("Starting timers...", game_timeleft);

			my.update_game_timeout();
			my.update_turn_timeout();
		}
		else
			game_timeleft = my.sp_session_duration;
	}

	my.reset_timeout = function(){
		return;
	}

	self.update_game_timeout = function(){
		//console.log("game timeout: ", game_timeleft);

		if( game_timeleft < 0 )
			return;

		if( game_timeleft > 0 )
			game_timeleft -= 1;

		// timeout has occured!
		if( game_timeleft == 0 ){
			clicked_quit();
			goto_alert_screen("Session Timout!", "Sorry! Your time is up.", 3500);
		}

		if( my.inactivity_timeout < 0 )
			$("#game_timeout").css("display", "none" );
		else
			$("#game_timeout").css("display", "inline" );

		$("#game_timeout").html( "Session time remaining: " + normalizeTime(game_timeleft));

		setTimeout( "self.update_game_timeout()", 1000 );
	}

	self.update_turn_timeout = function(){
		//console.log("turn timeout: ", turn_timeleft);
		if( turn_timeleft < 0 || global.activePlayers.length > 1){
			$("#turn_timeout").css("display", "none" );
			return;
		}
		else
			$("#turn_timeout").css("display", "inline" );

		//ignore inactivity timeout when it's not your turn.
		if (global.currentTurn != position){
			$("#turn_timeout").css("display", "none" );
			return;
		}

		if( turn_timeleft > 0 )
			turn_timeleft -= 1;

		if( my.turn_timeleft == 0 ){
			timeout_count++;
			HookboxConnection.hookbox_conn.publish('faceclick', [-1, -1] );
			goto_alert_screen("Timeout!", "You have not made a move in time. Your turn has gone to another player.", 3500);
		}

		if (timeout_count == my.mp_timeout_limit){
			clicked_quit();
			turn_timeleft = -1;
			goto_alert_screen("Timeout!", "", 3500);
		}

		if( turn_timeleft < 0 )



		$("#turn_timeout").html( "Time remaining for your turn " + normalizeTime(turn_timeleft) );

		setTimeout("self.update_turn_timeout()",1000); // call me again in 1000 ms
	}

	my.update_game_timeout = self.update_game_timeout;
	my.update_turn_timeout = self.update_turn_timeout;

	function normalizeTime(t){
		return Math.floor(t/60).toString() + ":" + (t%60 < 10 ? ("0" + t%60).toString() : (t%60).toString());
	}

	return my;
}(jQuery))

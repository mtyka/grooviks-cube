// GAME TIMOUT COUNTER & LOGIC

var timeout = (function($){
	var self = this;

	var my = {};

	my.mp_timeout_limit = 2;
	my.mp_turn_duration	= 32;
	my.sp_session_duration = 321;
	my.mp_session_duration = 321;
	my.menu_timeout = 10;
	my.inactivity_timeout_length = 30;

	var turn_timeleft = -1;
	var timeout_count =  0;
	var game_timeleft = -1;
	var inactivityTimeLeft = -1;

	var gameTimer = null;
	var turnTimer = null;
	var menuTimer = null;
	var inactiveTimer = null;

	my.getTimeleft = function(){
		return [turn_timeleft, timeout_count, game_timeleft];
	}

//------ SYNC GAME TIMER -------
	my.set_game_time = function(actual){
		game_timeleft = actual;
	}

	my.get_game_timeleft = function(){
		return game_timeleft;
	}

	my.get_game_time = function(){
		HookboxConnection.hookbox_conn.publish('info', {'get': 'timeout'});
	}

//------ START TIMERS -------
	my.start_game_timer = function(){
		if (client_state = "MULTIPLE")
			game_timeleft = my.mp_session_duration;
		else
			game_timeleft = my.sp_session_duration;

		if (!gameTimer)
			gameTimer = setInterval("self.update_game_timeout()", 1000);
		else{
			clearInterval(gameTimer);
			gameTimer = setInterval("self.update_game_timeout()", 1000);
		}

		my.get_game_time();
		setTimeout(my.get_game_time, Math.floor(game_timeleft/2));
		$("#game_timeout").css("display", "inline");
	}

	my.start_turn_timer = function(){
		if (turnTimer != null || global.activePlayers.length <= 1){
			return;
		}

		turn_timeleft = my.mp_turn_duration;

		if (!turnTimer)
			turnTimer = setInterval("self.update_turn_timeout()", 1000);
		else{
			clearInterval(turnTimer);
			turnTimer = setInterval("self.update_turn_timeout()", 1000);
		}

		$("#turn_timeout").css("display", "inline");
	}

	my.start_menu_timer = function(){
		if (menuTimer != null){
			return;
		}
		else{
			menuTimer = setTimeout(function(){
				if (menu.menustate == 0)
					return;
				console.log("MENU TIMEOUT!");
				clearTimeout(menuTimer);
				menuTimer = null;

				if (menu.menustate == 9){
					HookboxConnection.hookbox_conn.publish('vote', {'position':position, 'vote':0});
					menu.clear_screen();
				}
				else{
					menu.clicked_quit();
				}

			}, my.menu_timeout * 1000);
		}
	}

	my.start_inactivity_timer = function(){
		if (inactiveTimer == null){
			console.log('inactiveity timer starterd');
			inactivityTimeLeft = my.inactivity_timeout_length;
			inactiveTimer = setInterval(self.update_inactivity_timeout, 1000);;
		}
	}

//------ STOP TIMERS -------
	my.stop_game_timer = function(){
		game_timeleft = -1;
		clearInterval(gameTimer);

		gameTimer = null;
		$("#game_timeout").css("display", "none");
	}

	my.stop_turn_timer = function(){
		turn_timeleft = -1;
		clearInterval(turnTimer);

		turnTimer = null;
		$("#turn_timeout").css("display", "none");
	}

	my.stop_menu_timer = function(){
		if (menuTimer != null){
			clearTimeout(menuTimer);
			menuTimer = null;
		}
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

	my.reset_inactivity_timeout = function(){
		if (inactiveTimer == null){
			start_inactivity_timer();
		}
		else {
			inactivityTimeLeft = my.inactivity_timeout_length;
		}
	}

//------ UPDATE TIMERS -------
	self.update_game_timeout = function(){

		if (game_timeleft <= 0){
			menu.goto_alert_screen("Timeout!", "Sorry your time is up.", 3500, true);

			my.stop_game_timer();
			return;
		}

		game_timeleft -= 1;

		if (game_timeleft % 60 == 0 && game_timeleft > 0)
			HookboxConnection.hookbox_conn.publish('info', {'get': 'timeout'});

		$("#game_timeout").html("Session time remaining " + global.normalizeTime(game_timeleft));
	}

	self.update_turn_timeout = function(){
		if (global.currentTurn != position || global.activePlayers.length <= 1){
			if (global.activePlayers.length > 1){
				CubeControl.ignore_clicks = true;
			}
			my.stop_turn_timer();
			return;
		}
		else if (turn_timeleft <= 0){
			timeout_count += 1;
			if (timeout_count == my.mp_timeout_limit){
				menu.clicked_quit();
				menu.goto_alert_screen("Timeout!", "", 3500, true);

				my.stop_turn_timer();
				timeout_count = 0;
				return;
			}
			else{
				HookboxConnection.hookbox_conn.publish('faceclick', [-1, -1] );
				menu.goto_alert_screen("Timeout!", "You have not made a move in time. Your turn has gone to another player.", 3500, false);

				my.stop_turn_timer();
				return;
			}
		}

		turn_timeleft -= 1;

		$("#turn_timeout").html("Time remaining for your turn " + global.normalizeTime(turn_timeleft));
	}

	self.update_inactivity_timeout = function(){
		if (global.activePlayers.length == 1){
			if (menu.menustate != 0){
				//do not decrement if any menu is showing, like a request to join menu or such.
				return;
			}
			else if (inactivityTimeLeft <= 0){
				menu.clicked_quit();
				clearInterval(inactiveTimer);
				inactiveTimer = null;
			}
			else if (inactivityTimeLeft > 0){
				inactivityTimeLeft -= 1;
			}
			console.log("inactive: " + inactivityTimeLeft);
		}
		// else{
		// 	inactiveTimerStarted = false;
		// 	clearInterval(inactiveTimer);
		// 	inactiveTimer = null;
		// }
	}

	my.update_game_timeout = self.update_game_timeout;
	my.update_turn_timeout = self.update_turn_timeout;

	return my;
}(jQuery))

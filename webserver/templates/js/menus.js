// menu.js
// menu state manager and functions

menu = (function(){

	var self = this;

	var my = {};

	my.menustate = 0;
	my.quitClicked = false;

	var interrupt_ok = true;
	var waitingTimer = null;

	// 1 = no menu
	// 2 = mode menu
	// 3 = level menu
	// 4 = timeout menu
	// 5 = join    menu
	// 6 = queued  menu
	// 7 = waiting menu
	// 8 = connecting menu;
	// 9 = vote menu
	// 10= alert screen, a menu style alert that enters and dismisses quickly.
	// 11= victory menu

	var menuIds = {
		1: "#idlemenu", 2: "#modemenu", 	3: "#levelmenu", 	4: "#timeoutmenu",
		5: "#joinmenu", 6: "#queuedmenu", 	7: "#waitingmenu", 	8: "#connectingmenu",
		9: "#votemenu", 10: "#alertmenu", 	11: "#victorymenu"};


	function reset_gamestate(position, difficulty) {
		console.log("Resetting gamestate: " + difficulty);
		HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'SELECT_DIFFICULTY', 'difficulty' : difficulty});
	}

	var selected_game_mode = "START_3P"


	function flyin_menu_bg(){
		// background is in place - thus ignore clicks on canvas
		CubeControl.ignore_clicks=true;

		hide_rotation_buttons();
	}

	function flyout_menu_bg(){

	}

	function flyin_menu( id ){
		$(id).css("left", "-25%");
		$(id).css("display", "inline");
		$(id).animate( {
		  left: "0%",
		},{ duration: 1000,
			complete: function(){
				CubeControl.ignore_clicks = true;
			}
		});

		if ([0,1,6,7,8].indexOf(my.menustate) == -1)
			timeout.start_menu_timer();
	}

	function flyout_menu( id ){
		$(id).animate( {
			left: "125%"
		},{ duration: 1000,
			complete: function(){
				$(id).css("left", "-25%");
				$(id).css("display", "none");
			}
		});
		timeout.stop_menu_timer();
	}

	function menuIsOpen(m){
		return $(menuIds[m]).css('display') == "inline";
	}

	function disableButton(which, disabled){
		if (disabled)
			$(which).attr("disabled", "disabled");
		else
			$(which).removeAttr("disabled");
	}

		my.select_difficulty  = function (difficulty){

		global.difficulty = difficulty;

		last_moves_from_solved = difficulty
		moves_from_solved = difficulty
		//next_flash_moves_display = setTimeout("flash_moves_display()", 5000 );

		console.log("diff etc: ", difficulty, game_state);
		//HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );

		if (difficulty > 0){
			reset_gamestate(position, difficulty);
		}

		// This is somewhat hacky - but because of the order reversal in multiplayer mode compared to single player mode,
		// the select diff screen has to clear itself in multiplayer mode. But not in single player mode.
		console.log("Gamestate? " + game_state );
		if( game_state == "MULTIPLE" ){
			my.clear_screen();
		}
		else{
			console.log("single?");
		}
		timeout.start_game_timer();
		setTimeout(function(){set_initial_position();}, 400);
	}

	my.goto_idle_screen = function(){
		CubeControl.ignore_clicks = true;
		if( my.menustate == 1 && menuIsOpen(1)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 1
			flyin_menu("#idlemenu");

			$("#button_quit, #button_perspective").css( "opacity", 0.5);
			disableButton("#button_quit, #button_perspective", true);

			$("#turn_notice").animate( { opacity:0.0 },{ duration: 1000 });

			interrupt_ok = true;

			console.log("setting client state to home-restart");

			start_spin( true );
	}

	my.goto_mode_screen = function(){
		CubeControl.ignore_clicks = true;
		if( my.menustate == 2 && menuIsOpen(2)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 2
			flyin_menu("#modemenu");

			interrupt_ok = true;

			start_spin( true );
	}

	my.goto_level_screen = function(){
		console.log("goto_level_screen()");
			CubeControl.ignore_clicks = true;
		if( my.menustate == 3 && menuIsOpen(3)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 3
			flyin_menu("#levelmenu");

			start_spin( true );
	}

	my.goto_timeout_screen = function(){
		CubeControl.ignore_clicks = true;
		if( my.menustate == 4 && menuIsOpen(4)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 4
			flyin_menu("#timeoutmenu");
			start_spin( true );
	}

	my.goto_join_screen = function(){
		CubeControl.ignore_clicks = true;
		if( my.menustate == 5 && menuIsOpen(5)) return;
			if( interrupt_ok ){
				remove_menu();
				if( my.menustate == 0 ) flyin_menu_bg();
				my.menustate = 5
				flyin_menu("#joinmenu");
			}

			global.difficultyNotice(true);

			start_spin( true );
	}

	my.goto_queued_screen = function(){
		console.log("goto_queued_screen()");
			CubeControl.ignore_clicks = true;
		if( my.menustate == 6 && menuIsOpen(6)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 6
			flyin_menu("#queuedmenu");

			start_spin( true );
			timeout.get_game_time();
			setTimeout( function(){ //give it some time to respond
				$("#timeUntilTurn").html(global.normalizeTime(timeout.get_game_timeleft()));
				waitingTimer = setInterval("self.waitTick()", 1000);
			}, 1500);
	}

	my.goto_waiting_screen = function(){
		console.log("goto_waiting_screen()");
		CubeControl.ignore_clicks = true;
		if( my.menustate == 7 && menuIsOpen(7)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 7
			flyin_menu("#waitingmenu");

			start_spin( true );
	}

	my.goto_connecting_screen = function(){
		CubeControl.ignore_clicks = true;
		if( my.menustate == 8 && menuIsOpen(8)) return;
			remove_menu();
			if( my.menustate == 0 ) flyin_menu_bg();
		my.menustate = 8
			flyin_menu("#connectingmenu");

			start_spin( true );
	}

	my.goto_vote_screen = function(){
		console.log("goto_vote_screen()");
		CubeControl.ignore_clicks = true;
		if( my.menustate == 9 && menuIsOpen(9)) return;
			remove_menu();

		my.menustate = 9;

		flyin_menu("#votemenu");

		start_spin( true );
	}

	my.voteYes = function(){
		HookboxConnection.hookbox_conn.publish('vote', {'position':position, 'vote':1});
		my.clear_screen();
	}

	my.voteNo = function(){
		HookboxConnection.hookbox_conn.publish('vote', {'position':position, 'vote':0});
		my.clear_screen();
	}

	my.goto_alert_screen = function(text, subtext, timeup, quit){
		console.log("goto_alert_screen()", text, subtext, timeup, quit);
		CubeControl.ignore_clicks = true;
		if( my.menustate == 10 && menuIsOpen(10)) return;
			remove_menu();

		flyin_menu_bg(); //there (should) never a menu up before this one
		my.menustate = 10;

		$("#alertmenu h1").html(text);
		$("#alertmenu h2").html(subtext);

		flyin_menu("#alertmenu");

		if (quit)
			setTimeout(function(){
				my.clicked_quit();
				$("#alertmenu h1").empty();
				$("#alertmenu h2").empty();
			}, timeup);
		else
			setTimeout(function(){
				my.clear_screen();
				$("#alertmenu h1").empty();
				$("#alertmenu h2").empty();
				global.turnCheck();
			}, timeup);
	}

	my.goto_victory_screen = function(){
		console.log("goto_victory_screen(), yay!");
		CubeControl.ignore_clicks = true;
		if( my.menustate == 11 && menuIsOpen(11)) return;
			remove_menu();

		my.menustate = 11;

		flyin_menu("#victorymenu");

		var val = timeout.get_game_timeleft();
		var upper = 500;

		if (client_state == "MULT"){
			upper = timeout.mp_session_duration;
		}
		else{
			upper = timeout.sp_session_duration;
		}

		$("#victoryTime").html(global.normalizeTime(upper - val));
		$("#victoryDiff").html(global.parseDifficulty());

		timeout.stop_game_timer();
		timeout.stop_turn_timer();

		start_spin( true );

		setTimeout(function(){
			my.clicked_quit();
		}, 10000);
	}


	function remove_menu(){
		flyout_menu(menuIds[my.menustate]);

		if (my.menustate == 0){
			show_rotation_buttons();
			if (global.activePlayers.length > 1)
				global.difficultyNotice(true);
			else
				global.difficultyNotice(false);
		}
		else{
			hide_rotation_buttons();
		}
	}

	function show_rotation_buttons(){
		$("#buttonleft, #buttonright").css('display', 'inline');
	}

	function hide_rotation_buttons(){
		$("#buttonleft, #buttonright").css('display', 'none');
	}

	my.clear_screen = function(){
		remove_menu();

		if( game_state == "MULTIPLE" ){
			timeout.start_game_timer();
			show_rotation_buttons();
			global.turnCheck();
		}
		else if( game_state == "SINGLE" ){
			timeout.start_game_timer();
			show_rotation_buttons();
			global.currentTurn = position;
		}

		$("#button_quit, #button_perspective").css("opacity", 1.0);
		disableButton("#button_quit, #button_perspective", false);

		$("#turn_notice").animate( { opacity:1.0 },{ duration: 500 });

		set_initial_position();

		my.menustate = 0;
		console.log("menu state set to 0");
	}

	self.waitTick = function(){
		var timeStr = $("#timeUntilTurn").html();
		if (timeStr == "")
			return;

		timeStr = timeStr.split(":");

		var val = parseInt(timeStr[0]*60) + parseInt(timeStr[1]);

		if (!menuIsOpen(6)){
			clearInterval(waitingTimer);
			waitingTimer == null;
			return;
		}

		if (val <= 0 || global.activePlayers.length == 0){
			clearInterval(waitingTimer);
			waitingTimer == null;
			my.goto_level_screen();
		}
		else {
			val -= 1;
			if (val % 60 == 0 && val > 0)
				HookboxConnection.hookbox_conn.publish('info', {'get': 'timeout'});

			$("#timeUntilTurn").html(global.normalizeTime(val));
		}
	}
	my.waitTick = self.waitTick;

	my.clicked_quit = function (){
		console.log("ClientSent: QUIT ");
		HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'QUIT' } );
		my.quitClicked = true;

		setTimeout(function(){my.quitClicked = false;}, 1400);

		timeout.stop_game_timer();
		timeout.stop_turn_timer();
		timeout.stop_menu_timer();

		if (waitingTimer != null){
			clearInterval(waitingTimer);
			waitingTimer == null;
		}

		global.turnCheck();

		global.difficultyNotice(false);
		my.goto_idle_screen();
	}

	my.clicked_wake = function (){
		console.log("ClientSent: WAKE ");
		HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'WAKE' } );

		global.turnCheck();
	}

	my.clicked_alone= function (){
		selected_game_mode = "START_1P";
		my.goto_level_screen( );
	}

	my.clicked_3player= function (){
		selected_game_mode = "START_3P";
		console.log("ClientSentGameMode: " + selected_game_mode );
		HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );
		my.goto_level_screen( )
	}

	my.clicked_send_join_request = function(){
		HookboxConnection.hookbox_conn.publish('vote', {'vote-initiate' : position} );
		my.goto_waiting_screen();
	}

	my.clicked_ignore = function (){
		interrupt_ok = false;
		my.clear_screen()
	}

	my.clicked_join = function (){
		my.clear_screen()
		//not implemented yet
		HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'JOIN_3P' } );
	}

	my.clicked_continue = function (){
		timeout.start_game_timer();
		my.clear_screen();
	}

	return my;
})()
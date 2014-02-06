// menu.js
// menu state manager and functions

var interrupt_ok=true;
var menustate = 0;
var quitClicked = false;
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

function reset_gamestate(position, difficulty) {
    console.log("Resetting gamestate: " + difficulty);
    HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'SELECT_DIFFICULTY', 'difficulty' : difficulty});
}

var selected_game_mode = "START_3P"

function select_difficulty( difficulty ){

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
		clear_screen();
	}
	else{
		console.log("single?");
	}
	timeout.start_game_timeout();
	setTimeout(function(){set_initial_position();}, 400);
}


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
	},{ duration: 1000 }
	);

	CubeControl.ignore_clicks = true;
}

function flyout_menu( id ){
	$(id).animate( {
	  left: "125%"
	},{ duration: 1000,
		complete: function(){
			$(id).css("left", "-25%");
			$(id).css("display", "none");
		}
	  }
	);
}

function flyin_idlemenu() {
}

function flyout_idlemenu() {
}

function goto_idle_screen(){
    CubeControl.ignore_clicks = true;
   	if( menustate == 1 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 1
		flyin_menu("#idlemenu");

		$("#button_quit, #button_perspective").css( "opacity", 0.5);
		disableButton("#button_quit, #button_perspective", true);

		$("#turn_notice").animate( { opacity:0.0 },{ duration: 1000 });

		interrupt_ok = true;

		console.log("setting client state to home-restart");

		start_spin( true );
}

function disableButton(which, disabled){
	if (disabled)
		$(which).attr("disabled", "disabled");
		$(which).
	else
		$(which).removeAttr("disabled");
}

function goto_mode_screen(){
	CubeControl.ignore_clicks = true;
   	if( menustate == 2 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 2
		flyin_menu("#modemenu");

		interrupt_ok = true;

		start_spin( true );
}

function goto_level_screen(){
    console.log("goto_level_screen()");
		CubeControl.ignore_clicks = true;
   	if( menustate == 3 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 3
		flyin_menu("#levelmenu");

		start_spin( true );
}

function goto_timeout_screen(){
    CubeControl.ignore_clicks = true;
   	if( menustate == 4 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 4
		flyin_menu("#timeoutmenu");
		start_spin( true );
}

function goto_join_screen(){
    CubeControl.ignore_clicks = true;
   	if( menustate == 5 ) return;
		if( interrupt_ok ){
			remove_menu();
			if( menustate == 0 ) flyin_menu_bg();
			menustate = 5
			flyin_menu("#joinmenu");
		}

		global.difficultyNotice(true);

		start_spin( true );
}

function goto_queued_screen(){
    console.log("goto_queued_screen()");
		CubeControl.ignore_clicks = true;
   	if( menustate == 6 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 6
		flyin_menu("#queuedmenu");

		start_spin( true );
		timeout.get_game_time();
		$("#timeUntilTurn").html(timeout.get_real_game_timeleft());
		waitTimer = setInterval("waitTick()", 1000);
}

function goto_waiting_screen(){
    console.log("goto_waiting_screen()");
    CubeControl.ignore_clicks = true;
   	if( menustate == 7 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 7
		flyin_menu("#waitingmenu");

		start_spin( true );
}

function goto_connecting_screen(){
    CubeControl.ignore_clicks = true;
   	if( menustate == 8 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 8
		flyin_menu("#connectingmenu");

		start_spin( true );
}

function goto_vote_screen(){
	CubeControl.ignore_clicks = true;
   	if( menustate == 9 ) return;
		remove_menu();

   	menustate = 9;

	flyin_menu("#votemenu");

	start_spin( true );
}

function voteYes(){
	HookboxConnection.hookbox_conn.publish('vote', {'position':position, 'vote':1});
	clear_screen();
}

function voteNo(){
	HookboxConnection.hookbox_conn.publish('vote', {'position':position, 'vote':0});
	clear_screen();
}

function goto_alert_screen(text, subtext, timeup){
	CubeControl.ignore_clicks = true;
   	if( menustate == 10 ) return;
		remove_menu();

	flyin_menu_bg(); //there is never a menu up before this one
   	menustate = 10;

	$("#alertmenu h1").html(text);
	$("#alertmenu h2").html(subtext);

	flyin_menu("#alertmenu");

	start_spin( true );

	setTimeout(function(){
		clear_screen();				//depends on the context, might want to quit()
		$("#alertmenu h1").empty();
		$("#alertmenu h2").empty();
	}, timeup);
}

function goto_victory_screen(){
	CubeControl.ignore_clicks = true;
   	if( menustate == 11 ) return;
		remove_menu();

   	menustate = 11;

	flyin_menu("#victorymenu");

	var timeStr = timeout.get_real_game_timeleft();
	timeStr = timeStr.split(":");

	var val = parseInt(timeStr[0]*60) + parseInt(timeStr[1]);
	var upper = 500;

	if (client_state == "MULT"){
		upper = timeout.mp_session_duration;
	}
	else{
		upper = timeout.sp_session_duration;
	}

	$("#victoryTime").html(normalizeTime(upper - val));
	$("#victoryDiff").html(global.parseDifficulty());

	timeout.stop_game_timer();
	timeout.stop_turn_timer();

	start_spin( true );

	setTimeout(function(){
		clicked_quit();
	}, 10000);
}


function remove_menu(){
	if( menustate == 1 )   flyout_menu("#idlemenu");
	else if( menustate == 2 )   flyout_menu("#modemenu");
	else if( menustate == 3 )   flyout_menu("#levelmenu");
	else if( menustate == 4 )   flyout_menu("#timeoutmenu");
	else if( menustate == 5 )   flyout_menu("#joinmenu");
	else if( menustate == 6 )   flyout_menu("#queuedmenu");
	else if( menustate == 7 )   flyout_menu("#waitingmenu");
	else if( menustate == 8 )   flyout_menu("#connectingmenu");
	else if( menustate == 9 )   flyout_menu("#votemenu");
	else if( menustate == 10 )  flyout_menu("#alertmenu");
	else if( menustate == 11 )  flyout_menu("#victorymenu");

	if (menustate == 0){
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

function clear_screen(){
	remove_menu();

	if( game_state == "MULTIPLE" ){
		timeout.start_game_timeout();
		show_rotation_buttons();
		global.turnCheck();
	}
	if( game_state == "SINGLE" ){
		timeout.start_game_timeout();
		show_rotation_buttons();
		global.currentTurn = position;
	}

	$("#button_quit, #button_perspective").css("opacity", 1.0);
	disableButton("#button_quit, #button_perspective", false);

	$("#turn_notice").animate( { opacity:1.0 },{ duration: 500 });

	menustate = 0;
	console.log("menu state set to 0");
	set_initial_position();
}

function waitTick(){
	var timeStr = $("#timeUntilTurn").html();
	timeStr = timeStr.split(":");

	var val = parseInt(timeStr[0]*60) + parseInt(timeStr[1]);

	if (val <= 0 || global.activePlayers.length == 0){
		clearInterval(waitTimer);
		waitTimer == null;
		goto_level_screen();
	}
	else {
		val -= 1;
		$("#timeUntilTurn").html(normalizeTime(val));
	}
}

function normalizeTime(t){
	return Math.floor(t/60).toString() + ":" + (t%60 < 10 ? ("0" + t%60).toString() : (t%60).toString());
}

function clicked_quit(){
	console.log("ClientSent: QUIT ");
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'QUIT' } );
	quitClicked = true;
	setTimeout(function(){quitClicked = false;}, 1400);

	timeout.stop_game_timer();
	timeout.stop_turn_timer();

	if (waitingTimer){
		clearInterval(waitingTimer);
		waitingTimer == null;
	}

	global.turnCheck();

	global.difficultyNotice(false);
}

function clicked_wake(){
	console.log("ClientSent: WAKE ");
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'WAKE' } );

	global.turnCheck();
}

function clicked_alone(){
	selected_game_mode = "START_1P";
	goto_level_screen( );
}

function clicked_3player(){
	selected_game_mode = "START_3P";
	console.log("ClientSentGameMode: " + selected_game_mode );
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );
	goto_level_screen( )
}

function clicked_send_join_request(){
	HookboxConnection.hookbox_conn.publish('vote', {'vote-initiate' : position} );
	goto_waiting_screen();
}

function clicked_ignore(){
	interrupt_ok = false;
	clear_screen()
}

function clicked_join(){
	clear_screen()
    //not implemented yet
    HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'JOIN_3P' } );
}

function clicked_continue(){
	timeout.start_game_timeout();
	clear_screen();
}


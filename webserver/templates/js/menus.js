// menu.js
// menu state manager and functions

var interrupt_ok=true;
var menustate = 0;
var quitClicked = false;

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

function reset_gamestate(position, difficulty) {
    console.log("Resetting gamestate: " + difficulty);
    HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'SELECT_DIFFICULTY', 'difficulty' : difficulty});
}

var selected_game_mode = "START_3P"
function select_difficulty( difficulty ){

	last_moves_from_solved = difficulty
	moves_from_solved = difficulty
	next_flash_moves_display = setTimeout("flash_moves_display()", 5000 );

	clog("ClientSentGameMode: " + selected_game_mode );
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );
  	if (difficulty > 0){
  		reset_gamestate(position, difficulty );
		set_initial_position();
	}

	timeout.clear_game_timeout();

	// This is somewhat hacky - but because of the order reversal in multiplayer mode compared to single player mode,
	// the select diff screen has to clear itself in multiplayer mode. But not in single player mode.
	clog("Gamestate? " + game_state );
	if( game_state == "MULT" ){
		clear_screen();
	}
}


function flyin_menu_bg(){
	// background is in place - thus ignore clicks on canvas
	CubeControl.ignore_clicks=true;

	hide_rotation_buttons();
	//hide_instructions();
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
		$("#button_quit").animate( { opacity:0.0 },{ duration: 1000 });
		$("#button_perspective").animate( { opacity:0.0 },{ duration: 1000 });

		interrupt_ok = true;

		clog("setting client state to home-restart");
		timeout.clear_timeout();
		start_spin( true );
}

function goto_mode_screen(){
	CubeControl.ignore_clicks = true;
   	if( menustate == 2 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 2
		flyin_menu("#modemenu");

		interrupt_ok = true;
		timeout.clear_timeout();
		start_spin( true );
}

function goto_level_screen(){
    clog("goto_level_screen()");
		CubeControl.ignore_clicks = true;
   	if( menustate == 3 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 3
		flyin_menu("#levelmenu");
		timeout.clear_timeout();
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
		timeout.clear_timeout();
		start_spin( true );
}

function goto_queued_screen(){
    clog("goto_queued_screen()");
		CubeControl.ignore_clicks = true;
   	if( menustate == 6 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 6
		flyin_menu("#queuedmenu");
		timeout.clear_timeout();
		start_spin( true );
}

function goto_waiting_screen(){
    clog("goto_waiting_screen()");
    CubeControl.ignore_clicks = true;
   	if( menustate == 7 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 7
		flyin_menu("#waitingmenu");
		timeout.clear_timeout();
		start_spin( true );
}

function goto_connecting_screen(){
    CubeControl.ignore_clicks = true;
   	if( menustate == 8 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 8
		flyin_menu("#connectingmenu");
		timeout.clear_timeout();
		start_spin( true );
}

function goto_vote_screen(){
	CubeControl.ignore_clicks = true;
   	if( menustate == 9 ) return;
		remove_menu();

	flyin_menu_bg(); //there is never a menu up before this one
   	menustate = 9;

	flyin_menu("#votemenu");
	timeout.clear_timeout();
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

	$("#alertmenu h2").html(text);
	$("#alertmenu h4").html(subtext);

	flyin_menu("#alertmenu");
	timeout.clear_timeout();
	start_spin( true );

	setTimeout(function(){
		clear_screen();
		$("#alertmenu h2").empty();
		$("#alertmenu h4").empty();
	}, timeup);
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

	if (menustate == 0){
		show_rotation_buttons();
	}
	else{
		hide_rotation_buttons();
	}
}

function show_instructions(){
	$(".instructions").css("display", "inline")
}

function hide_instructions(){
	$(".instructions").css("display", "none")
}

function show_rotation_buttons(){
	$("#buttonleft, #buttonright").css('display', 'inline');
}

function hide_rotation_buttons(){
	$("#buttonleft, #buttonright").css('display', 'none');
}

function clear_screen(){
	remove_menu()
	if( menustate != 0 )
		flyout_menu_bg();

	menustate=0
	set_initial_position();

	// trigger greeting flash
	hide_rotation_buttons();
	//hide_instructions();
	if( game_state == "MULTIPLE" ){
		timeout.start_timeout();
  		//flash_display("Welcome to the 3-Player Game", 8000);
		//show_instructions();
		show_rotation_buttons();
		global.turnCheck();
	}
	if( game_state == "SINGLE" ){
		timeout.start_timeout();
		//flash_display("Welcome to the Single Player Game", 8000 );
		show_rotation_buttons();
		global.currentTurn = position;
	}

	$("#button_quit").animate( {opacity:1.0},{ duration: 1000 });
	$("#button_perspective").animate( { opacity:1.0 },{ duration: 1000 });
}

function clicked_quit(){
	clog("ClientSent: QUIT ");
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'QUIT' } );
	quitClicked = true;
	setTimeout(function(){quitClicked = false;}, 1400);
}

function clicked_wake(){
	clog("ClientSent: WAKE ");
	HookboxConnection.hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'WAKE' } );

	global.turnCheck();
}

function clicked_alone(){
	selected_game_mode = "START_1P";
	goto_level_screen( )
}

function clicked_3player(){
	selected_game_mode = "START_3P";
	clog("ClientSentGameMode: " + selected_game_mode );
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
	timeout.start_timeout();
	clear_screen();
}


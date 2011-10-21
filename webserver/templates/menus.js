


// Set up the click handlers
$(document).ready(function(){
    $("#easy").click(   function() { select_difficulty(2);  } );
    $("#medium").click( function() { select_difficulty(3);  } );
    $("#hard").click(   function() { select_difficulty(4);  } );
    $("#master").click( function() { select_difficulty(5);  } );
    $("#full").click(   function() { select_difficulty(20); } );

//    //if (!position) {
        $("#buttonleft").click( function(){
           animate_spin( -Math.PI*2/3 );
        });
        $("#buttonright").click( function(){
           animate_spin( Math.PI*2/3 );
        });
//    } else {
//    $("#buttonleft, #buttonright").css('visibility', 'hidden');
//    }

});


var selected_game_mode = "START_3P"
function select_difficulty( difficulty ){

	last_moves_from_solved = difficulty
	moves_from_solved = difficulty
	next_flash_moves_display = setTimeout("flash_moves_display()", 5000 );

	clog("ClientSentGameMode: " + selected_game_mode );
	hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );
  reset_gamestate(position, difficulty );

	set_initial_position();
	clear_game_timeout();
	
	// THis is somewhat hacky - but because of the order reversal in multiplayer mode compared to single player mode, 
	// the select diff screen has to clear itself in multiplayer mode. But not in single player mode.
	clog("Gamestate? " + game_state );
	if( game_state == "MULT" ){
		clear_screen();
	}
}


function flyin_menu_bg(){
		// background is in place - thus ignore clicks on canvas
		ignore_clicks=true;

		// animate all the opacities and positions to bring in the background of the menu
		$("#levelmenu_bg").css("opacity", "-2.0");
		$("#levelmenu_bg").css("left", "0");
		$("#levelmenu_bgb").css("opacity", "-2.0");
		$("#levelmenu_bgt").css("opacity", "-2.0");

		$("#levelmenu_bgb").animate( {
			opacity:1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bgt").animate( {
			opacity:1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bg").animate( {
			opacity:0.6
		},{ duration: 1000 }
		);

		$("#button_restart").animate( {
			opacity:0.0
		},{ duration: 1000 }
		);
		ignore_clicks = true;

		hide_rotation_buttons();
		hide_instructions();
}

function flyout_menu_bg(){
		$("#levelmenu_bgb").animate( {
			opacity:-1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bgt").animate( {
			opacity:-1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bg").animate( {
			opacity:-1.0
		},{ duration: 1000
		//, complete: function(){ } //  $("#levelmenu_bg").css("left", "-100%") }   }
		
		} );
		$("#button_restart").animate( {
			opacity:1.0
		},{ duration: 1000 }
		);
}

function flyin_menu( id ){
		$(id).css("left", "-25%");
		$(id).css("display", "inline");
		$(id).animate( {
		  left: "50%",
		},{ duration: 1000 }
		);
		//$("#levelmenu_bg").css("left", "0");
		$("#levelmenu_bgb").animate( {
			opacity:1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bgt").animate( {
			opacity:1.0
		},{ duration: 1000 }
		);
		$("#levelmenu_bg").animate( {
			opacity:0.6
		},{ duration: 1000 }
		);
		ignore_clicks = true;
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
    ignore_clicks = true;
   	if( menustate == 1 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 1
		flyin_menu("#idlemenu");
		$("#button_quit").animate( { opacity:0.0 },{ duration: 1000 });

		interrupt_ok = true;

		clog("setting client state to home-restart");
		clear_timeout();
		start_spin( true );
}

function goto_mode_screen(){
	ignore_clicks = true;
   	if( menustate == 2 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 2
		flyin_menu("#modemenu");

		interrupt_ok = true;
		clear_timeout();
		start_spin( true );
}

function goto_level_screen(){
    clog("goto_level_screen()");
		ignore_clicks = true;
   	if( menustate == 3 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 3
		flyin_menu("#levelmenu");
		clear_timeout();
		start_spin( true );
}

function goto_timeout_screen(){
    ignore_clicks = true;
   	if( menustate == 4 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 4
		flyin_menu("#timeoutmenu");
		start_spin( true );
}

function goto_join_screen(){
    ignore_clicks = true;
   	if( menustate == 5 ) return;
		if( interrupt_ok ){
			remove_menu();
			if( menustate == 0 ) flyin_menu_bg();
			menustate = 5
			flyin_menu("#joinmenu");
		}
		clear_timeout();
		start_spin( true );
}

function goto_queued_screen(){
    clog("goto_queued_screen()");
		ignore_clicks = true;
   	if( menustate == 6 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 6
		flyin_menu("#queuedmenu");
		clear_timeout();
		start_spin( true );
}

function goto_waiting_screen(){
    clog("goto_waiting_screen()");
    ignore_clicks = true;
   	if( menustate == 7 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 7
		flyin_menu("#waitingmenu");
		clear_timeout();
		start_spin( true );
}

function goto_connecting_screen(){
    ignore_clicks = true;
   	if( menustate == 8 ) return;
		remove_menu();
		if( menustate == 0 ) flyin_menu_bg();
   	menustate = 8
		flyin_menu("#connectingmenu");
		clear_timeout();
		start_spin( true );
}


function remove_menu(){
		if( menustate == 1 )   flyout_menu("#idlemenu");
		if( menustate == 2 )   flyout_menu("#modemenu");
		if( menustate == 3 )   flyout_menu("#levelmenu");
		if( menustate == 4 )   flyout_menu("#timeoutmenu");
		if( menustate == 5 )   flyout_menu("#joinmenu");
		if( menustate == 6 )   flyout_menu("#queuedmenu");
		if( menustate == 7 )   flyout_menu("#waitingmenu");
		if( menustate == 8 )   flyout_menu("#connectingmenu");

		if( menustate == 1 ) {
			$("#button_quit").animate( {
				opacity:1.0
			},{ duration: 1000 }
			);
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
		if( menustate != 0 ) flyout_menu_bg();
    menustate=0
		ignore_clicks=false;
		set_initial_position();

		// trigger greeting flash
		hide_rotation_buttons();
		hide_instructions();
		if( game_state == "MULTIPLE" ){
			start_timeout();
      flash_display("Welcome to the 3-Player Game", 8000);
			show_instructions();
		}
		if( game_state == "SINGLE" ){
			start_timeout();
			flash_display("Welcome to the Single Player Game", 8000 );
			show_rotation_buttons();
		}
}


function clicked_quit(){
		clog("ClientSent: QUIT ");
		hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'QUIT' } );
}

function clicked_wake(){
		clog("ClientSent: WAKE ");
		hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'WAKE' } );
}

function clicked_alone(){
	  selected_game_mode = "START_1P";
		goto_level_screen( )
}

function clicked_3player(){
	  selected_game_mode = "START_3P";
		clog("ClientSentGameMode: " + selected_game_mode );
		hookbox_conn.publish('clientcommand', {'position' : position, 'command' : selected_game_mode } );
	  //goto_level_screen( )
}

function clicked_ignore(){
	  interrupt_ok = false;
	  clear_screen()
}

function clicked_join(){
	  clear_screen()
    //not implemented yet
    hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'JOIN_3P' } );
}


function clicked_continue(){
	start_timeout();
	clear_screen();
}


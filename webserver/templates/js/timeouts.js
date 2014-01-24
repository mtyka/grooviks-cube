// GAME TIMOUT COUNTER & LOGIC

var timeout = (function($){
	var self = this;

	var my = {};

	my.inactivity_timeout_length = 40;
	my.inactivity_timeout = -1; // off by default

	my.mp_timeout_limit = 2;
	my.mp_turn_duration	= 30;
	my.sp_session_duration = 240;
	my.mp_session_duration = 240;
	my.menu_timeout = 10;

	function game_timeout_occured() {
		clicked_quit();
	}

	my.clear_game_timeout = function(){
		game_timeout = -2;
		$("#game_timeout").css("display", "none" );
	}

	self.count_down_game_timeout = function(){
		if( game_timeout > -2 )
			game_timeout -= 1;

		// timeout has occured!
		if( game_timeout == -1 )
			game_timeout_occured();

		if( game_timeout < 0 )
			$("#game_timeout").css("display", "none" );
		else
			$("#game_timeout").css("display", "inline" );

		$("#game_timeout").html( normalizeTime(game_timeout) );

		setTimeout( "self.count_down_game_timeout()", 1000 );
	}

	my.clear_timeout = function (){
		clog( "Clear inactivity timeout..." );
		my.inactivity_timeout = -1;
	}

	my.start_timeout = function(){
		clog( "Starting timeout: ", my.inactivity_timeout_length );
		my.inactivity_timeout = my.inactivity_timeout_length;
	}

	my.reset_timeout = function (){
		// dont allow resets when you're already in the menu that asks you to continue
		// also dont allow resets when the timer is off (i.e. inactivity_timeout < 0 )
		// otherwise this call will erroneously switch on the timer when that's not desired.
		if ( menustate != 4 && timeout.inactivity_timeout >= 0 )
			my.inactivity_timeout = my.inactivity_timeout_length;
	}

	self.update_timeout = function(){

		//ignore inactivity timeout when it's not your turn.
		if (global.currentTurn != position){
			return;
		}

		if( my.inactivity_timeout >= 0 && my.inactivity_timeout <= 10 &&  menustate == 0 ){
			//Only show timeout menu when we're not already in some menu
			goto_timeout_screen();
		}

		//document.title = inactivity_timeout;
		// Fulltimeout

		if( my.inactivity_timeout == 0 )
			clicked_quit();

		if( my.inactivity_timeout >= 0 )
			$("#timeout_display").html( my.inactivity_timeout );
		else
			$("#timeout_display").html( 0 );


		if( my.inactivity_timeout > -2 )
			my.inactivity_timeout-=1;

		setTimeout("self.update_timeout()",1000); // call me again in 1000 ms
	}

	my.update_timeout = self.update_timeout;

	function normalizeTime(t){
		return Math.floor(t/60).toString() + ":" + (t%60 < 10 ? ("0" + t%60).toString() : (t%60).toString());
	}

	$(document).ready(function(){
		// Add a click event that resets the timeouts
		$(window).bind( "click touchstart", function( eventObj ) {
			my.reset_timeout();
		});

		// start the timeout counters
		// update_timeout();
		self.count_down_game_timeout();
	});

	return my;
}(jQuery))

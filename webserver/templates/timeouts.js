
// GAME TIMOUT COUNTER & LOGIC 

function clear_game_timeout(){
	game_timeout = -2;
	$("#game_timeout").css("display", "none" );
}

function count_down_game_timeout(){
	if( game_timeout > -2 ) game_timeout -= 1;
	
	// timeout has occured!
	if( game_timeout == -1 ){
		game_timeout_occured();
	}
	if( game_timeout < 0 ) $("#game_timeout").css("display", "none" )
	else                   $("#game_timeout").css("display", "inline" )
	$("#game_timeout").html( game_timeout );
	
	setTimeout( "count_down_game_timeout()", 1000 );
}

var game_timeout_display = $( jQuery( '<div class="game_timeout"> <h1 id="game_timeout" >Timeout</h1> </div>' ) )

$( document ).ready( function(){
		$( "body" ).append( game_timeout_display )
		
		// start the timeout counters
		//update_timeout();
		count_down_game_timeout(); 
} );






var inactivity_timeout_length = 20; 
var inactivity_timeout = -1; // off by default 

function clear_timeout(){
	clog( "Clear inactivity timeout..." );
	inactivity_timeout = -1;
}
function start_timeout(){
	clog( "Starting timeout: ", inactivity_timeout_length );
	inactivity_timeout = inactivity_timeout_length;
}

function reset_timeout(){
	// dont allow resets when you're already in the menu that asks you to continue
	// also dont allow resets when the timer is off (i.e. inactivity_timeout < 0 )
	// otherwise this call will erroneously switch on the timer when that's not desired.
	if ( menustate != 4 && inactivity_timeout >= 0 ) inactivity_timeout = inactivity_timeout_length;
}

function update_timeout( ){
	//clog("Update_timeout: " + inactivity_timeout );
	if( inactivity_timeout >= 0 && inactivity_timeout <= 10 ){ 
		//Only show timeout menu when we're not already in some menu
		if( menustate == 0 ) goto_timeout_screen(); 
	}
	
	document.title = inactivity_timeout 
	// Fulltimeout
	
	if( inactivity_timeout == 0 ){ clicked_quit(); } 
	
	if( inactivity_timeout >= 0 ){
		$("#timeout_display").html( inactivity_timeout );
	}else{
		$("#timeout_display").html( 0 );
	}

	if( inactivity_timeout > -2 ) inactivity_timeout-=1;
	setTimeout("update_timeout()",1000) // call me again in 1000 ms
}




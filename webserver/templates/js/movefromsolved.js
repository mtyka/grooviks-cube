
//////////// FLASH DISPLAY ////////////////////////////////////////////

function flash_display( text ){
	flash_display( test, 6000 );
}

function flash_display( text, uptime ){
	$("#movestext").css("opacity", "0.0");
	$("#movestext").html( text );
	$("#movestext").animate( {
		opacity:1.0
	},{ duration: 1000 }
	);
	setTimeout( "remove_flash_display()", uptime )
}

function remove_flash_display(){
	$("#movestext").animate( {
		opacity:0.0
	},{ duration: 1000,
	    complete: function() { $("#movestext").html(""); } }
	);

}


///////////// HOW MANY MOVES FROM SOLVED - DISPLAY ////////////////////
var last_moves_from_solved = 0
var moves_from_solved = 0
var next_flash_moves_display;
function flash_moves_display(){
	// exclude when not to flash moves display
	if ( client_state != "MULT" && client_state != "SING" ) return;
	if ( client_state == "SING" && ( active_position != position) ) return;
	if( moves_from_solved  <= 0 ) return;
	if( moves_from_solved > 5 ) return;
	if( (moves_from_solved > last_moves_from_solved) &&
	    ( moves_from_solved >  -1 ) &&
			( last_moves_from_solved > -1 )
	){
		if( moves_from_solved == 1 ) flash_display("Hey! It was so pristine - now you've messed it up!" );
		if( moves_from_solved == 2 ) flash_display("Looks like that was wrong. You're now " + moves_from_solved + " moves away from solved!");
		if( moves_from_solved == 3 ) flash_display("Hmmm.. 3 moves from solved");
		if( moves_from_solved == 4 ) flash_display("Wrong direction - you're now 4 moves away from solved.");
		if( moves_from_solved == 5 ) flash_display("Believe it or not - You're now " + moves_from_solved + " moves from solved!");
	}
	else if ( moves_from_solved == last_moves_from_solved ){
		flash_display("You're just " + moves_from_solved + " moves from solved!");
	}else{
		if( moves_from_solved == 1 ) flash_display("Just one more move !" );
		if( moves_from_solved == 2 ) flash_display("So close! Just " + moves_from_solved + " moves from solved!");
		if( moves_from_solved == 3 ) flash_display("Nice! Only " + moves_from_solved + " moves from solved!");
		if( moves_from_solved == 4 ) flash_display("Ok, you're getting close now - you're " + moves_from_solved + " moves from solved!");
		if( moves_from_solved == 5 ) flash_display("Believe it or not - You're merely " + moves_from_solved + " moves from solved!");
	}
	last_moves_from_solved = moves_from_solved;
}

function reset_flash_moves_timeout(){
	clog( "Clear Flash Moves Timeout" );
	$("#movestext").html("");
}

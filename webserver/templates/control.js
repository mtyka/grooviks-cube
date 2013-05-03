
var client_state = "IDLE";
var game_state = "UNBOUND";
var active_position = 0;

var game_timeout = -2;
var inactivity_timeout = -1;
var ignore_clicks = false;
var locked_buttons=false;
var menustate = 0;
var interrupt_ok=true;
// 0 = no menu
// 1 = mode menu
// 2 = level menu
// 3 = timeout menu
// 4 = join    menu
// 5 = queued  menu
// 5 = waiting menu



// ####################################################################
// ######################## Control Logic #############################
// ####################################################################


// safe way to log things on webkit and not blow up firefox
function clog(msg) {
    if( window.console ) {
        console.log(msg);
    }
}


var previous_datagram = null;
var first_connection = true;

function on_message_pushed( datagram ) {
     $('#cube_status').html('Begin play.');
     $('#cube_status').animate({'opacity': 0}, 4000 );
			
		 if( first_connection ){
		   goto_idle_screen();
			 first_connection = false
		 }

		 current_cube_colors = decompress_datagram( datagram );
		 if( previous_datagram != datagram ) {
			 reset_arrow_timer();
			 previous_datagram = datagram;
		 }
		 update_view();  // calls into the renderer code
}


function game_timeout_occured() {
	clicked_quit();	
}


function on_game_state_change(newState, activePosition, clientstate) {
//     game_state = newState
     $('#game_state').val( newState )
     $('#active_position').val( activePosition )
    
		 active_position = activePosition;
		 var old_client_state = client_state;
		 new_client_state = clientstate[position-1];
		 new_game_state = newState;

     clog("ActivePlayer: " + active_position + "MyPosition: " + position );
		 clog("Server: NewState:" + new_client_state + "OldState: " + client_state ); 
		 clog("Server: NewGameState:" + new_game_state + "OldGameState: " + game_state ); 
		
		 reset_timeout();
		
		 var old_game_state = game_state;
		 game_state = new_game_state;
		 
			 client_state = new_client_state;
			 if ( client_state == "IDLE" ){
				 clear_game_timeout();
				 goto_idle_screen();
			 } else
			 if ( client_state == "HOME" ){
				 clear_game_timeout();
				 goto_mode_screen();
			 } else
			 if ( client_state == "SING" ){
			
				 if( game_state == "SINGLE_INVITE" ){
           goto_join_screen();
				 } else
				 if( game_state == "SINGLE" ){
     			 clog("Deciding on Single player: ActivePlayer: " + active_position + "MyPosition: " + position );
           if ( active_position == position ){
							if( old_game_state != new_game_state ){
								game_timeout=180;
							}
							clear_screen();
				 	 } else {
							goto_queued_screen();
					 }
				 } else
				 if( game_state == "VICTORY" ){
					 clear_game_timeout();
           clear_screen();
				 }
			 
			 } else
			 if ( client_state == "MULT" ){
			
				 if( game_state == "SINGLE_INVITE" ){
					 clear_game_timeout();
           goto_waiting_screen();
				 } else
				 if( game_state == "MULTIPLE" ){
					 // active player gets to select difficulty mode.
					 if ( new_client_state == "MULT" && old_client_state == "HOME" ){ 
						 goto_level_screen( )   // create level screen
					 } 
					 else 
					 // active player comes from a waiting screen
					 if ( new_client_state == "MULT" && old_client_state == "MULT" && old_game_state == "SINGLE_INVITE"  ){
						 goto_level_screen( )   // create level screen
					 }
					 else {
						 clear_game_timeout();  // no timeout in 3 player mode
						 clear_screen();        // got to game
					 }

				 } else
				 if( game_state == "VICTORY" ){
           clear_screen();
				 }
			 
			 } else
			 if ( client_state == "VICT" ){
				 clear_screen();
			 }else{
				 clog("Unknown client_state:" + client_state );
			 }



}


// Converts a long hex string into an array of 54 RGB-float-triples
function decompress_datagram(datagram) {
    //clog("decompressing...");
    //clog(datagram);
    var output = [];

    while( datagram.length > 0 ) {
        var rgb = datagram.substring(0,6);
        datagram = datagram.substring(6);
        output[output.length] = parse_hex_rgb(rgb);
    }
    //clog("decompressed to...");
    //clog(output);
    return output;
}

function parse_hex_rgb(hexstring) {
    var rgb_floats = [];
    for(i=0; i<3; i++) {
      var rgbhex = hexstring.substring(i*2, 2 + i*2);
      var rgbint = parseInt(rgbhex,16);
      rgb_floats[i] = rgbint / 255.0;
    }
    return rgb_floats;
}



//
// Logic to turn arrows off when moving
//

var INCLUDE_ARROWS = false;

var enable_arrows_timeout = null;


function reset_arrow_timer() {
    INCLUDE_ARROWS = false;
    clearTimeout( enable_arrows_timeout );
    enable_arrows_timeout = setTimeout( show_arrows, HOW_LONG_STABLE_BEFORE_SHOWING_ARROWS );
}

function show_arrows() {
    INCLUDE_ARROWS = true;
    update_view();
}



//
// rendering stuff
//


function update_view() {
   // looks at the view sliders and renders-the cube with that and the current color-state
   var altitude = $("#slide_alt").val() / 100.0;
   var azimuth = $("#slide_azi").val() / 100.0;
   var height = $('#canvas').attr('height');
   var width = $('#canvas').attr('width');
   render_view(height, width, altitude, azimuth, 15 );
   //window.setTimeout( update_view, 50 );

   frames_rendered ++;
}





function set_ignore_clicks( value ){
	ignore_clicks = value;
}

function rotate_view() {
    clear_svg();
    update_view();
}

 $(document).ready( function() {
    // Draw the cube in its default state when the page first loads
    update_view();

		$("body").click( function( eventObj ) {
			reset_timeout();
			if( !ignore_clicks ){
				 //var x = eventObj.pageX;
				 //var y = eventObj.pageY;
				 //clog("local click at absolute ("+x+","+y+")");

				 var top_left_canvas_corner = $("#canvas").elementlocation();
				 var x = eventObj.pageX - top_left_canvas_corner.x;
				 var y = eventObj.pageY - top_left_canvas_corner.y;

				 //clog("local click at relative ("+x+","+y+")");

				 cube_got_clicked_on(x,y);
			
				 return true;
			}
		});
});

var faceclick_subscription;
var lastFaceClicked = -1;
var renderClickedFaceCount = 0;

function cube_got_clicked_on(x,y) 
{
    facenum = whichFaceIsPointIn(x,y);
    if( facenum < 0 )
	{
     	// not on a cube face
     	clog("Local click not on cube face.");
     	return;
    }
    //faceclick_subscription.publish( facenum );  // docs say this should work but it doesn't
    if (shouldDrawArrow(facenum)) {
        clog("Publishing local click on face "+facenum);
      	var rotation_direction = arrowRotation[facenum][0] > 0;
      	// See QueueRotation in groovik.py
      	// TODO(bretford): mapping is weird, fix
      	var rotation_index = arrowRotation[facenum][1] + (Math.abs(arrowRotation[facenum][0]))%3*3;
      	hookbox_conn.publish('faceclick', [facenum, rotation_index, rotation_direction] );
    
		if ( INCLUDE_ARROWS )
		{
			lastFaceClicked = facenum;
			renderClickedFaceCount = 5;
		}
	}
}

function reset_gamestate(position, difficulty) {
    clog("Resetting gamestate: " + difficulty);
    hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'SELECT_DIFFICULTY', 'difficulty' : difficulty});
}



// ####################################################################
// ######################## Cube clicks and drawing ###################
// ####################################################################


CubeControl = (function($){
  my = {}

my.ignore_clicks = false;
my.lastFaceClicked = -1;
my.renderClickedFaceCount = 0;
my.INCLUDE_ARROWS = false;
my.admin_mode = false;
var current_mode;
var previous_datagram = null;
var faceclick_subscription;
var enable_arrows_timeout = null;





my.update_cube_state_from_datagram = function( datagram ) {
		 current_cube_colors = decompress_datagram( datagram );
		 if( previous_datagram != datagram ) {
			 reset_arrow_timer();
			 previous_datagram = datagram;
		 }
		 my.update_view();  // calls into the renderer code
}



// Converts a long hex string into an array of 54 RGB-float-triples
function decompress_datagram(datagram) {
    //console.log("decompressing...");
    //console.log(datagram);
    var output = [];

    while( datagram.length > 0 ) {
        var rgb = datagram.substring(0,6);
        datagram = datagram.substring(6);
        output[output.length] = parse_hex_rgb(rgb);
    }
    //console.log("decompressed to...");
    //console.log(output);
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


function reset_arrow_timer() {
    my.INCLUDE_ARROWS = false;
    clearTimeout( enable_arrows_timeout );
    enable_arrows_timeout = setTimeout( show_arrows, HOW_LONG_STABLE_BEFORE_SHOWING_ARROWS );
}

function show_arrows() {
    if(!my.admin_mode){
      my.INCLUDE_ARROWS = true;
    }
    my.update_view();
}



//
// rendering stuff
//


my.update_view = function() {
   // looks at the view sliders and renders-the cube with that and the current color-state
   var altitude = $("#slide_alt").val() / 100.0;
   var azimuth = $("#slide_azi").val() / 100.0;
   var height = $('#canvas').attr('height');
   var width = $('#canvas').attr('width');
   render_view(height, width, altitude, azimuth, 15 );
   frames_rendered ++;
}


function set_ignore_clicks( value ){
	my.ignore_clicks = value;
}


function cube_got_clicked_on(x,y) 
{
    facenum = whichFaceIsPointIn(x,y);
    if( facenum < 0 )
	  {
     	// not on a cube face
     	console.log("Local click not on cube face.");
     	return;
    }
    if (shouldDrawArrow(facenum) || my.admin_mode ) {
        console.log("Publishing local click on face "+facenum);
      	var rotation_direction = arrowRotation[facenum][0] > 0;
      	// See QueueRotation in groovik.py
      	// TODO(bretford): mapping is weird, fix
      	var rotation_index = arrowRotation[facenum][1] + (Math.abs(arrowRotation[facenum][0]))%3*3;
      	HookboxConnection.hookbox_conn.publish('faceclick', [facenum, rotation_index, rotation_direction] );
    
		if ( my.INCLUDE_ARROWS )
		{
			my.lastFaceClicked = facenum;
			renderClickedFaceCount = 5;
		}
	}
}
 
 // set up events
 $(document).ready( function() {
    // Draw the cube in its default state when the page first loads
    my.update_view();

    // add click events that control the cube.
    $("body").click( function( eventObj ) {
			if(eventObj.shiftKey) {
			    	//Shift-Click

				 var top_left_canvas_corner = $("#canvas").elementlocation();
				 var x = eventObj.pageX - top_left_canvas_corner.x;
				 var y = eventObj.pageY - top_left_canvas_corner.y;

				 console.log("local shift click at relative ("+x+","+y+")");

				 cube_got_shift_clicked_on(x,y);
			
				 return true;
  		} 
			else if( !my.ignore_clicks ){
				 var top_left_canvas_corner = $("#canvas").elementlocation();
				 var x = eventObj.pageX - top_left_canvas_corner.x;
				 var y = eventObj.pageY - top_left_canvas_corner.y;

				 console.log("local click at relative ("+x+","+y+")");

				 cube_got_clicked_on(x,y);
			
				 return true;
			}
		});
});

  // public function update view
  my.rotate_view = function() {
      clear_svg();
      my.update_view();
  }

  return my; // return public members
}(jQuery))


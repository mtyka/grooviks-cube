
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

function on_message_pushed( datagram ) {
     $('#cube_status').html('Begin play.');
     $('#cube_status').animate({'opacity': 0}, 4000 );

     //clog("Got message published");
     //clog( datagram );
     current_cube_colors = decompress_datagram( datagram );
     if( previous_datagram != datagram ) {
        reset_arrow_timer();
        previous_datagram = datagram;
     }
     update_view();  // calls into the renderer code
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
    var int;
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

function rotate_view() {
    clear_svg();
    update_view();
}

 $(document).ready( function() {
    // Draw the cube in its default state when the page first loads
    update_view();

    $("#canvas").click( function( eventObj ) {
       //var x = eventObj.pageX;
       //var y = eventObj.pageY;
       //clog("local click at absolute ("+x+","+y+")");

       var top_left_canvas_corner = $("#canvas").elementlocation();
       var x = eventObj.pageX - top_left_canvas_corner.x;
       var y = eventObj.pageY - top_left_canvas_corner.y;

       //clog("local click at relative ("+x+","+y+")");

       cube_got_clicked_on(x,y);
    });
});

var faceclick_subscription;

function cube_got_clicked_on(x,y) {
    facenum = whichFaceIsPointIn(x,y);
    if( facenum < 0 ) {
      // not on a cube face
      clog("Local click not on cube face.");
      return;
    }
    clog("Publishing local click on face "+facenum);
    //faceclick_subscription.publish( facenum );  // docs say this should work but it doesn't
    if (arrowRotation[facenum] != 0) {
      rotation_direction = arrowRotation[facenum][0] > 0;
      // See QueueRotation in groovik.py
      // TODO(bretford): mapping is weird, fix
      rotation_index = arrowRotation[facenum][1] + (Math.abs(arrowRotation[facenum][0]))%3*3;
      hookbox_conn.publish( 'faceclick', [facenum, rotation_index, rotation_direction] );
    }
}


// ####################################################################
// #################### Communications Setup ##########################
// ####################################################################

var hookbox_conn = null;
var subscription = null;


function establish_hookbox_connections() {
    if( !is_hookbox_loaded ) {
        alert("Failed to connect to hookbox server.");
    }

    // create a connection object and setup the basic event callbacks.
    hookbox_conn = hookbox.connect(server);
    //hookbox_conn.onOpen = function() { alert("connection established!"); };
    hookbox_conn.onError = function(err) { alert("Failed to connect to hookbox server: " + err.msg); };

    subscription = null;
    hookbox_conn.onSubscribed = function(channelName, _subscription) {
        if( channelName == 'iframe' ) {
            subscription = _subscription;                
            subscription.onPublish = function(frame) {
                on_message_pushed( frame.payload )
            };  
        }
        if( channelName == 'faceclick' ) {
            faceclick_subscription = _subscription;                
            faceclick_subscription.onPublish = function(frame) {
                clog('Heard about click on face ' + frame.payload);
            };  
        }
    };

   // Subscribe to the pubsub channel with the colors
   hookbox_conn.subscribe("iframe");
   hookbox_conn.subscribe("faceclick");
}




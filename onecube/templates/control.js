
// ####################################################################
// ######################## Control Logic #############################
// ####################################################################


function on_message_pushed( datagram ) {
     //console.log("Got message published");
     //console.log( datagram );
     current_cube_colors = decompress_datagram( datagram );
     update_view();  // calls into the renderer code
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
    var int;
    for(i=0; i<3; i++) {
      var rgbhex = hexstring.substring(i*2, 2 + i*2);
      var rgbint = parseInt(rgbhex,16);
      rgb_floats[i] = rgbint / 255.0;
    }
    return rgb_floats;
}

function update_view() {
   // looks at the view sliders and renders-the cube with that and the current color-state
   var altitude = $("#slide_alt").val() / 100.0;
   var azimuth = $("#slide_azi").val() / 100.0;
   render_view(300, 300, altitude, azimuth, 15 );
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
       //console.log("local click at absolute ("+x+","+y+")");

       var top_left_canvas_corner = $("#canvas").elementlocation();
       var x = eventObj.pageX - top_left_canvas_corner.x;
       var y = eventObj.pageY - top_left_canvas_corner.y;

       //console.log("local click at relative ("+x+","+y+")");

       cube_got_clicked_on(x,y);
    });
});

var faceclick_subscription;

function cube_got_clicked_on(x,y) {
    facenum = whichFaceIsPointIn(x,y);
    if( facenum < 0 ) {
      // not on a cube face
      console.log("Local click not on cube face.");
      return;
    }
    console.log("Publishing local click on face "+facenum);
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

// create a connection object and setup the basic event callbacks.
// finally, subcribe to "chan1".
//var hookbox_conn = hookbox.connect('http://127.0.0.1:2974');
var hookbox_conn = hookbox.connect(server);
//hookbox_conn.onOpen = function() { alert("connection established!"); };
hookbox_conn.onError = function(err) { alert("Failed to connect to hookbox server: " + err.msg); };

var subscription = null;
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
            console.log('Heard about click on face ' + frame.payload);
        };  
    }
};

$(document).ready(function() {
   // Subscribe to the pubsub channel with the colors
   hookbox_conn.subscribe("iframe");
   hookbox_conn.subscribe("faceclick");
});




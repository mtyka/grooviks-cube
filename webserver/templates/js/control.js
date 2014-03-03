// ####################################################################
// ######################## Cube clicks and drawing ###################
// ####################################################################


CubeControl = (function($){
	var my = {}

	my.ignore_clicks = false;
	my.lastFaceClicked = -1;
	my.renderClickedFaceCount = 0;
	my.drawArrows = false;
	my.admin_mode = false;

	var current_mode;
	var previous_datagram = null;
	var faceclick_subscription;
	var enable_arrows_timeout = null;
	var faceJustClicked = false;
	var timeIdleUntilShowArrows = 200;	// ms

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
	my.reset_arrow_timer = function() {
		my.drawArrows = false;
		clearTimeout( enable_arrows_timeout );
		enable_arrows_timeout = setTimeout( show_arrows, timeIdleUntilShowArrows);
	}

	my.cube_got_clicked_on = function(x,y) {
		if ( my.ignore_clicks)
			return;

		facenum = Renderer.whichFaceIsPointIn(x,y);
		if( facenum < 0 ){
			// not on a cube face
			console.log("Local click not on cube face.");
			return;
		}
		if ( (Renderer.shouldDrawArrow(facenum) || my.admin_mode) && !faceJustClicked) {
			console.log("Publishing local click on face "+facenum);
			var rotation_direction = arrowRotation[facenum][0] > 0;
			// See QueueRotation in groovik.py
			// TODO(bretford): mapping is weird, fix
			var rotation_index = arrowRotation[facenum][1] + (Math.abs(arrowRotation[facenum][0]))%3*3;
			HookboxConnection.hookbox_conn.publish('faceclick', [facenum, rotation_index, rotation_direction] );

			faceJustClicked = true;
			setTimeout(function(){faceJustClicked = false;}, 750);

			if ( my.drawArrows ){
				my.lastFaceClicked = facenum;
				renderClickedFaceCount = 5;
			}
			timeout.stop_turn_timer();
		}
	}

	my.update_view = function() {
		// looks at the view sliders and renders-the cube with that and the current color-state
		var altitude = $("#slide_alt").val() / 100.0;
		var azimuth = $("#slide_azi").val() / 100.0;
		var height = $('#canvas').attr('height');
		var width = $('#canvas').attr('width');
		Renderer.render_view(height, width, altitude, azimuth, 15 );
		frames_rendered ++;
	}

	function show_arrows() {
		if(!my.admin_mode){
			my.drawArrows = true;
		}
		//console.log("show arrows called");

		Renderer.alphaTransition = 0.0;
		$("#alphaTransition").attr('avalue', 0);

		//animate arrows into existence
		$("#alphaTransition").stop();
		$("#alphaTransition").animate(
		{
			avalue: 1.0
		},{	duration: 250,
			complete: function(){
				Renderer.alphaTransition = 1.0;
				my.update_view();
			},
			step: function(){
				//console.log($("#alphaTransition").attr("avalue"));
				Renderer.alphaTransition = parseFloat($("#alphaTransition").attr("avalue"));
				my.update_view();
			}
		});
	}

	my.set_ignore_clicks = function( value ){
		my.ignore_clicks = value;
	}

	my.update_cube_state_from_datagram = function( datagram ) {
		Renderer.set_current_cube_colors(decompress_datagram( datagram ));
		if( previous_datagram != datagram ) {
				my.reset_arrow_timer();
				previous_datagram = datagram;
		}
		my.update_view();	// calls into the renderer code
	}

	return my; // return public members
}(jQuery))


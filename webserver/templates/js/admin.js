var max_slider = 1000;

function hexFromRGB(r, g, b) {
	var hex = [
		r.toString( 16 ),
		g.toString( 16 ),
		b.toString( 16 )
	];
	$.each( hex, function( nr, val ) {
		if ( val.length === 1 ) {
			hex[ nr ] = "0" + val;
		}
	});
	return hex.join( "" ).toUpperCase();
}

function refreshSwatch() {
	var red = $( "#red" ).slider( "value" ),
		green = $( "#green" ).slider( "value" ),
		blue = $( "#blue" ).slider( "value" ),
		hex = hexFromRGB( red, green, blue );
	//  Add your code here $( "#swatch" ).css( "background-color", "#" + hex );
	calibrateEvent();
}

$(function() {
	$( "#red, #green, #blue" ).slider({
		orientation: "horizontal",
		range: "min",
		max: max_slider,
		value: max_slider,
		slide: refreshSwatch,
		change: refreshSwatch
	});
});

var calibrationFace = -1;

function cube_got_shift_clicked_on(x,y){
    if ( CubeControl.current_mode == 1 ) {
        var facenum = Renderer.whichFaceIsPointIn(x,y);
        calibrationFace = facenum;
        HookboxConnection.hookbox_conn.publish('colorcalib', [facenum] );
        $('div#facenum').html('Facet ' + facenum + ' is now being calibrated.');
        console.log("Facet " + facenum + " is now being calibrated");
    }
}

function calibrate(face, red, green, blue) {
	console.log("Calibrating face: " + face +" r: " + red + " g: " + green + " b: " + blue);
	HookboxConnection.hookbox_conn.publish('colorcalib', [face, blue, green, red]);
}

function calibrateEvent(){
	if (calibrationFace == -1) {
		console.log("Escaping out of calibration because no face selected");
		return;
	}

	// TODO: (CWhite) Add mode check

	var red = $( "#red" ).slider( "value" ),
	green = $( "#green" ).slider( "value" ),
	blue = $( "#blue" ).slider( "value" );
	calibrate(calibrationFace ,red/max_slider, green/max_slider, blue/max_slider);
}

function changeSlider(rgb_floats){
        console.log("changing slider based on message" );
        $( "#red" ).slider( "value", rgb_floats[0]*max_slider);
        $( "#green" ).slider( "value", rgb_floats[1]*max_slider );
        $( "#blue" ).slider( "value", rgb_floats[2]*max_slider );
}

function set_cubemode(mode) {
    console.log("Setting cube mode: " + mode);
    console.log( HookboxConnection.hookbox_conn )
    HookboxConnection.hookbox_conn.publish('cubemode', {'mode' : mode});
    CubeControl.current_mode = mode;

    if (mode == 1)
        $("#calibration-sliders").show();
    else
    	$("#calibration-sliders").hide();

    if (mode == 2)
        $("#blankpixel").show();
    else
    	$("#blankpixel").hide();
}

function sendSettings(form){
	payload = {};
	payload["mp-turn-duration"] = form["mp-turn-duration"].value;
	payload["mp-timeout-limit"] = form["mp-timeout-limit"].value;
	payload["sp-session-duration"] = form["sp-session-duration"].value;
	payload["mp-session-duration"] = form["mp-session-duration"].value;
	payload["menu-timeout"] = form["menu-timeout"].value;
	console.log(payload);
	HookboxConnection.hookbox_conn.publish('settings', {'command': 'set', 'vals':payload});
}

function map_blank_pixel() {
    HookboxConnection.hookbox_conn.publish('faceclick', [54, 0, 0] );
}


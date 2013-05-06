
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



function cube_got_shift_clicked_on(x,y)
{
    if ( current_mode == 1 ) {
        var facenum = whichFaceIsPointIn(x,y);
        calibrationFace = facenum;   	
        HookboxConnection.hookbox_conn.publish('colorcalib', [facenum] );
        $('div#facenum').html('Face number ' + facenum + ' is now being calibrated.');
        clog("facenum " + facenum + " is now being calibrated");
    }
}

function calibrate(face, red, green, blue) {
	clog("Calibrating face: " + face +" r: " + red + " g: " + green + " b: " + blue);
	HookboxConnection.hookbox_conn.publish('colorcalib', [face, blue, green, red]);
}

function calibrateEvent()
{
	if (calibrationFace == -1) {
		clog("Escaping out of calibration because no face selected");
		return;
	}

	// TODO: (CWhite) Add mode check

	var red = $( "#red" ).slider( "value" ),
	green = $( "#green" ).slider( "value" ),
	blue = $( "#blue" ).slider( "value" );
	calibrate(calibrationFace ,red/max_slider, green/max_slider, blue/max_slider);     	
}
function changeSlider(rgb_floats){
        clog("changing slider based on message" );
        $( "#red" ).slider( "value", rgb_floats[0]*max_slider);
        $( "#green" ).slider( "value", rgb_floats[1]*max_slider );
        $( "#blue" ).slider( "value", rgb_floats[2]*max_slider );
}

function set_cubemode(mode) {
    clog("Setting cube mode: " + mode);
    clog( HookboxConnection.hookbox_conn )
    HookboxConnection.hookbox_conn.publish('cubemode', {'mode' : mode});
    current_mode = mode;

    if (mode == 1)
    {
        $("#calibration-sliders").show();
    }
    else
    {
    	$("#calibration-sliders").hide();	
    }
    if (mode == 2)
    {
        $("#blankpixel").show();
    }
    else
    {
    	$("#blankpixel").hide();	
    }
}

function map_blank_pixel() {
    HookboxConnection.hookbox_conn.publish('faceclick', [54, 0, 0] );
}
 

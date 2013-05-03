
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

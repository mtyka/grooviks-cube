/* general.js
 * To prevent inline-js pileup in the html page
 */
var last_move = 0;
var currentTurn = 0;
var delta_x = parseInt([ -Math.PI*2/3.01, 0, Math.PI*2/3.01 ][position-1] * 100);

//prevent scrolling on mobile pages
document.ontouchmove = function(e){
e.preventDefault();
}

//prevent highlighting
document.onselectstart = function (e){
return false;
}

//free rotation
$(document).bind("mousedown touchstart", function(e){
	last_move = e.pageX;
	$("#canvas").bind("mousemove touchmove", function(e){
		delta_x += e.pageX - last_move;
		last_move = e.pageX;
		$("#slide_azi").val(delta_x < 0 ? delta_x % -630 : delta_x % 630);
		CubeControl.update_view();
	});
});

$(document).bind("mouseup touchend", function(){
	$("#canvas").unbind();
	delta_x = delta_x < 0 ? delta_x % -630 : delta_x % 630; //uncertain why it's 630.
});

$(document).ready(function() {
	HookboxConnection.init( '/static/hookbox.js', function(){
	   goto_idle_screen();
	});

	currentTurn = position;

	goto_connecting_screen();
	update_timeout( );
	document.title = "P:" + position
});
/* general.js
 * To prevent inline-js pileup in the html page
 */
var global = (function($){
	var my = {};
	my.last_move = 0;
	my.currentTurn = 0;
	my.delta_x = parseInt([ -Math.PI*2/3.01, 0, Math.PI*2/3.01 ][position-1] * 100);

	my.turnCheck = function(){
		if (position != my.currentTurn)
			CubeControl.ignore_clicks = true;
		else if (menustate == 0)
			CubeControl.ignore_clicks = false;
	}

	//prevent scrolling on mobile pages
	$(document).bind("touchmove", function(e){
		e.preventDefault();
	});

	//prevent highlighting
	$(document).bind("selectstart", function(e){
		return false;
	});

	//free rotation
	$(document).bind("mousedown touchstart", function(e){
		my.last_move = e.pageX;
		$("#canvas").bind("mousemove touchmove", function(e){
			my.delta_x += e.pageX - my.last_move;
			my.last_move = e.pageX;
			$("#slide_azi").val(my.delta_x < 0 ? my.delta_x % -630 : my.delta_x % 630);
			CubeControl.update_view();
		});
	});

	$(document).bind("mouseup touchend", function(){
		$("#canvas").unbind();
		if (my.delta_x < 0)
			my.delta_x =  my.delta_x % -630
		else
			my.delta_x % 630; //uncertain why it's 630.
	});

	$(document).ready(function() {
		HookboxConnection.init( '/static/hookbox.js', function(){
		   goto_idle_screen();
		});

		my.currentTurn = position;

		goto_connecting_screen();
		update_timeout( );
		document.title = "P:" + position
	});

	return my;
}(jQuery))
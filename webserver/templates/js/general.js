/* general.js
 * To prevent inline-js pileup in the html page
 */
var kiosk = function(){
	spSessionDuration: 100;
	mpSessionDuration: 100;
	mpTurnDuration	:	50;
	mpTimeoutLimit	:	2;
	menuTimeout		: 	20;
}

var global = (function($){
	var my = {};
	my.last_move = 0;
	my.delta_x = parseInt([ -Math.PI*2/3.01, 0, Math.PI*2/3.01 ][position-1] * 100);
	my.currentTurn = 0;
	my.activePlayers = [];

	var wasSpinning = false;

	my.turnCheck = function(){
		if (position != my.currentTurn){
			CubeControl.ignore_clicks = true;
		}
		else if (menustate == 0){
			CubeControl.ignore_clicks = false;
		}

		//just to avoid a ton of hardcoding.
		var activeClass = "active";
		var onlineClass = "online";

		if (my.activePlayers.length == 0){
			$("#p1").removeClass(activeClass + " " + onlineClass);
			$("#p2").removeClass(activeClass + " " + onlineClass);
			$("#p3").removeClass(activeClass + " " + onlineClass);
		}
		else{
			for (var i=1; i <= 3; i++){
				if (my.activePlayers.indexOf(i) >= 0)
					$("#p"+i.toString()).addClass(onlineClass);
				else{
					$("#p"+i.toString()).removeClass(onlineClass);
					$("#p"+i.toString()).removeClass(activeClass)
				}
			}

			switch (parseInt(my.currentTurn)){
				case 1:
					$("#p1").addClass(activeClass);
					$("#p2").removeClass(activeClass);
					$("#p3").removeClass(activeClass);
					break;
				case 2:
					$("#p1").removeClass(activeClass);
					$("#p2").addClass(activeClass);
					$("#p3").removeClass(activeClass);
					break;
				case 3:
					$("#p1").removeClass(activeClass);
					$("#p2").removeClass(activeClass);
					$("#p3").addClass(activeClass);
					break;
				default:
					$("#p1").removeClass(activeClass + " " + onlineClass);
					$("#p2").removeClass(activeClass + " " + onlineClass);
					$("#p3").removeClass(activeClass + " " + onlineClass);
					console.log(my.currentTurn);
					break;
			}
		}
	}

	//add more to this later for the web version.
	my.isKiosk = function(){
		return true;
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
		//rotation only available when there are no menus
		if (menustate > 0)
			return;

		if (is_spinning){
			wasSpinning = true;
			stop_spin();
		}

		$("#slide_azi").stop();

		if (e.type == "mousedown"){
			my.last_move = e.pageX;

			$("#container").bind("mousemove", function(e){
				my.delta_x += e.pageX - my.last_move;
				my.last_move = e.pageX;
				$("#slide_azi").val(my.delta_x < 0 ? my.delta_x % -630 : my.delta_x % 630);
				CubeControl.update_view();
			});
		}
		else if (e.type == "touchstart"){
			//pageX is hidden in touches...?
		 	my.last_move = e.originalEvent.targetTouches[0].pageX;

			$("#container").bind("touchmove", function(e){
				my.delta_x += e.originalEvent.targetTouches[0].pageX - my.last_move;
				my.last_move = e.originalEvent.targetTouches[0].pageX;
				$("#slide_azi").val(my.delta_x < 0 ? my.delta_x % -630 : my.delta_x % 630);
				CubeControl.update_view();
			});
		}
	});

	$(document).bind("mouseup touchend", function(){
		$("#container").unbind();
		if (my.delta_x < 0)
			my.delta_x =  my.delta_x % -630
		else
			my.delta_x % 630; //uncertain why it's 630. /// it's close to 100*Math.PI*2

		if (wasSpinning){
			start_spin(true);
			wasSpinning = false;
		}

	});

	$(window).bind( "click touchstart", function() {
		timeout.reset_timeout();
		//touch screen to begin!
		if( menustate == 1 && !quitClicked){
			clicked_wake();
		}
	});

	$(document).ready(function() {

		HookboxConnection.init( '/static/hookbox.js', function(){
		   goto_idle_screen();
		});

		my.currentTurn = position;

		goto_connecting_screen();
		timeout.update_timeout( );
		document.title = "P:" + position

		//--------CubeControl on Ready-----------

		// Draw the cube in its default state when the page first loads
		CubeControl.update_view();

		// add click events that control the cube.
		$("body").bind( "click touchstart", function( eventObj ) {
			if( !CubeControl.ignore_clicks ){
				if (menustate > 0){
					CubeControl.ignore_clicks = true;
					return true;
				}

				var top_left_canvas_corner = $("#canvas").elementlocation();
				var x = eventObj.pageX - top_left_canvas_corner.x;
				var y = eventObj.pageY - top_left_canvas_corner.y;

				console.log("local click at relative ("+x+","+y+")");

				CubeControl.cube_got_clicked_on(x,y);

				return true;
			}
		});

		//--------menus on Ready-----------
		$("#easy").bind( "click touchstart",   function() { select_difficulty(2);  clear_screen(); set_initial_position();} );
		$("#medium").bind( "click touchstart", function() { select_difficulty(4);  clear_screen(); set_initial_position();} );
		$("#hard").bind( "click touchstart",   function() { select_difficulty(20); clear_screen(); set_initial_position();} );

		$("#buttonleft").bind( "click touchstart", function(){
			animate_spin( -Math.PI*2/3 );
		});

		$("#buttonright").bind( "click touchstart", function(){
			animate_spin( Math.PI*2/3 );
		});

		//--------loadhookbox on Ready-----------
		if( location.hash == "#debug" ) {
			$(".debug").css('display','block');
			setInterval( display_framerate, HOW_OFTEN_DISPLAY_FRAMERATE );
		}

		//--------Timeouts on Ready-----------
		// Add a click event that resets the timeouts
		$(window).bind( "click touchstart", function( eventObj ) {
			timeout.reset_timeout();
		});

		// start the timeout counters
		// update_timeout();
		timeout.count_down_game_timeout();
	});

	return my;
}(jQuery))
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

	my.difficulty = 0;

	var wasSpinning = false;

	my.turnCheck = function(){
		if (position != my.currentTurn){
			CubeControl.ignore_clicks = true;
		}
		else if (menustate == 0){
			setTimeout( function(){
				CubeControl.ignore_clicks = false;
				CubeControl.reset_arrow_timer();
			}, 1000);
			timeout.start_turn_timeout();
		}

		//just to avoid a ton of hardcoding.
		var activeClass = "active";
		var onlineClass = "online";

		if (my.activePlayers.length == 0){
			$("#p1").removeClass(activeClass + " " + onlineClass);
			$("#p2").removeClass(activeClass + " " + onlineClass);
			$("#p3").removeClass(activeClass + " " + onlineClass);
			tokenChanger();
		}
		else{
			for (var i=1; i <= 3; i++){
				if (my.activePlayers.indexOf(i) >= 0)
					$("#p"+i.toString()).addClass(onlineClass);
				else{
					$("#p"+i.toString()).removeClass(onlineClass);
				}
			}
		}
		if (my.currentTurn == position)
			$("#turn_notice").html("your turn").addClass('active');
		else
			$("#turn_notice").html("Player " + my.currentTurn + "'s turn").removeClass('active');

		tokenChanger();
	}

	my.parseDifficulty = function(){
		if (my.difficulty > 0 && my.difficulty <= 2)
			return "Easy";
		else if (my.difficulty > 2 && my.difficulty <= 4)
			return "Medium";
		else
			return "Hard";
	}

	my.difficultyNotice = function(on){
		if (on){
			$("#difficulty_notice").css("display", "inline");
			HookboxConnection.hookbox_conn.publish('difficulty', 'get');
		}
		else{
			$("#difficulty_notice").css("display", "none");
		}
	}

	function tokenChanger(){
		var file = "/static/turn-token/";
		var name = my.activePlayers.join("_");

		if (my.activePlayers.length == 1)
			name += "i";
		else if (my.activePlayers.length > 1){
			var ind = name.indexOf(my.currentTurn.toString());
			name = name.substr(0,ind+1) + "i" + name.substr(ind+1,name.length-1);
		}
		else if (my.activePlayers.length == 0){
			name = "0";
		}

		file += "cube_" + name + ".png";
		//console.log(file);
		$("#turn-token").attr('src', file);
	}

	//add more to this later for the web version.
	my.isKiosk = function(){
		return true;
	}

	my.unimplemented = function(){
		alert("Unimplemented");
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

		$("#slide_azi").stop(true, true);

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
		if( menustate == 1 && !quitClicked){
			clicked_wake();
		}
	});

 	my.insideout = false;

	$(document).ready(function() {

		HookboxConnection.init( '/static/hookbox.js', function(){
		   goto_idle_screen();
		   HookboxConnection.hookbox_conn.publish('settings', {'command': 'get'});
		});

		my.currentTurn = position;

		goto_connecting_screen();
		//timeout.update_game_timeout();
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
		$("#easy").bind( "click touchstart",   function() { select_difficulty(2);} );
		$("#medium").bind( "click touchstart", function() { select_difficulty(4);} );
		$("#hard").bind( "click touchstart",   function() { select_difficulty(20);} );

		$("#buttonleft").bind( "click touchstart", function(){
			console.log("button left click");
			animate_spin( -Math.PI*2/3 );
		});

		$("#buttonright").bind( "click touchstart", function(){
			console.log("button left click");
			animate_spin( Math.PI*2/3 );
		});

		//--------loadhookbox on Ready-----------
		if( location.hash == "#debug" ) {
			$(".debug").css('display','block');
			setInterval( display_framerate, HOW_OFTEN_DISPLAY_FRAMERATE );
		}
	});

	return my;
}(jQuery))
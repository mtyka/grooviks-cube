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

	my.recentEvent = false;

	var wasSpinning = false;
	var leaderboardOpen = false;
	var aboutOpen = false;
	var production = false;

	my.turnCheck = function(){
		if (position != my.currentTurn){
			CubeControl.ignore_clicks = true;
			$("#turn_notice").html("Player " + my.currentTurn + "'s turn").removeClass('active');
			toggleRotationButtons(false);
		}
		else{
			if (menu.menustate == 0 && global.activePlayers.length > 1){
				setTimeout( function(){
					CubeControl.ignore_clicks = false;
					CubeControl.reset_arrow_timer();
					timeout.start_turn_timer();
				}, 1000);
			}
			else if (menu.menustate == 0 && global.activePlayers.length == 1) {
				setTimeout( function(){
					CubeControl.ignore_clicks = false;
					if (!CubeControl.drawArrows)
						CubeControl.reset_arrow_timer();
				}, 1000);
				timeout.start_inactivity_timer();
			}
			$("#turn_notice").html("your turn").addClass('active');
			toggleRotationButtons(true);
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
			HookboxConnection.hookbox_conn.publish('info', {'get': 'difficulty'});
		}
		else{
			$("#difficulty_notice").css("display", "none");
		}
	}

	my.toggleLeaderboard = function(){
		if (leaderboardOpen)
			$('#leaderboard').css('display', 'none');
		else{
			$('#leaderboard').css('display', 'block');
			if (aboutOpen)
				my.toggleAbout();
		}

		leaderboardOpen = !leaderboardOpen;
	}

	my.toggleAbout = function(){
		if (aboutOpen)
			$('#about').css('display', 'none');
		else{
			$('#about').css('display', 'block');
			if (leaderboardOpen)
				my.toggleLeaderboard();
		}
		aboutOpen = !aboutOpen;
	}

	my.normalizeTime = function (t){
		return Math.floor(t/60).toString() + ":" + (t%60 < 10 ? ("0" + t%60).toString() : (t%60).toString());
	}

	function eventTimeout(){
		my.recentEvent = true;
		setTimeout(function(){my.recentEvent = false;}, 900);
	}

	function toggleRotationButtons(buttonsOn){
		var val = buttonsOn ? 1.0 : 0.3;
		$("#buttonleft").animate({opacity: val}, {duration: 200});
		$("#buttonright").animate({opacity: val}, {duration: 200});
	}

	// Image is determined by the active players array, joined together by '_'. An 'i' denotes the player's turn.
	// e.g. 'cube_1_2i.png' 'cube_1_2_3i.png'
	// If there is a 4th player (the web player), then the image does not change
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

		if (name.match(/4i|4/i))
			return;

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

 	my.insideout = false;

	$(document).ready(function() {

		HookboxConnection.init( '/static/hookbox.js', function(){
		   menu.goto_idle_screen();
		   HookboxConnection.hookbox_conn.publish('settings', {'command': 'get'});
		   HookboxConnection.hookbox_conn.publish('info', {'get': 'leaderboard'});
		   HookboxConnection.hookbox_conn.publish('info', {'get': '4thKiosk'});
		});

		my.currentTurn = position;

		// ------ Basic Bindings -------
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
			if (menu.menustate > 0)
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

		if (production){
			(function () {
			  var blockContextMenu, myElement;

			  blockContextMenu = function (evt) {
					evt.preventDefault();
			  };

			  window.addEventListener('contextmenu', blockContextMenu);
			})();
		}

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

		$("#svgholder, #idlemenu").bind( "click touchstart", function() {
			if (my.recentEvent || kioskLock)
				return;
			if( menu.menustate == 1 && !menu.quitClicked){
				menu.clicked_wake();
				eventTimeout();
			}
		});

		menu.goto_connecting_screen();
		//timeout.update_game_timeout();
		document.title = "P:" + position

		// Bottom Bar Bindings
		$('#button_leaderboard').bind('mousedown', function(){
			if (my.recentEvent)
				return;
			my.toggleLeaderboard();
			eventTimeout();
		});

		$('#button_about').bind('mousedown', function(){
			if (my.recentEvent)
				return;
			my.toggleAbout();
			eventTimeout();
		});

		//--------CubeControl on Ready-----------

		// Draw the cube in its default state when the page first loads
		CubeControl.update_view();

		// add click events that control the cube.
		$("body").bind( "mousedown touchstart", function( eventObj ) {
			if( !CubeControl.ignore_clicks ){
				if (menu.menustate > 0){
					CubeControl.ignore_clicks = true;
					return true;
				}

				var top_left_canvas_corner = $("#canvas").elementlocation();
				var x = eventObj.pageX - top_left_canvas_corner.x;
				var y = eventObj.pageY - top_left_canvas_corner.y;

				console.log("local click at relative ("+x+","+y+")");

				CubeControl.cube_got_clicked_on(x,y);

				if (my.activePlayers.length == 1){
					timeout.reset_inactivity_timeout();
				}

				return true;
			}
		});

		//--------menus on Ready-----------
		$("#easy").bind( "click touchstart",   function() {
			if (my.recentEvent)
				return;
			menu.select_difficulty(2); menu.clear_screen();
			eventTimeout()
		});
		$("#medium").bind( "click touchstart", function() {
			if (my.recentEvent)
				return;
			menu.select_difficulty(4); menu.clear_screen();
			eventTimeout()
		});

		$("#hard").bind( "click touchstart",   function() {
			if (my.recentEvent)
				return;
			menu.select_difficulty(20); menu.clear_screen();
			eventTimeout()
		});

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
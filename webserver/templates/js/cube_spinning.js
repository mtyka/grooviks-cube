

function set_initial_position(){
			// using -Math.PI*2/3 for the rotation angle gives a funny angle when rendered - I suspect there is a bug in render.js
      var start_azimuth = parseInt([ -Math.PI*2/3.01, 0, Math.PI*2/3.01 ][position-1] * 100);
        //clog('start azi: ' + start_azimuth);
        //$("#slide_azi").val(  start_azimuth );
        //CubeControl.update_view(); 
      clog("Resetting proper position: " + position + "  (" + start_azimuth + ")" );
			stop_spin();
			animate_absolute_spin( start_azimuth ) 
}

function animate_absolute_spin(radians) {
		// do the boogie 
		var azimuth = $("#slide_azi").val()*1.0; // convert from string to number. javascript sucks
		azimuth = azimuth % (100*Math.PI*2);  // Re-center
		$("#slide_azi").attr("animate_val", azimuth); // prep temporary animation variable
	
    clog("Animate_absolute_spin: " + azimuth + "    " + radians);
		if( azimuth == radians ){
			// we're already at solved position
			clog("Already at solved position");
			return;
		}
		
		locked_buttons = true;
    CubeControl.ignore_clicks = true;
		azimuth = radians 
		$("#slide_azi").animate( { 
			animate_val: azimuth 
		},{ duration: 2000, 
		    complete: function(){
					locked_buttons = false;
					CubeControl.ignore_clicks = false;
					CubeControl.update_view();
				},
				step: function() {  
					//console.log($("#slide_azi").attr("animate_val") ); 
					$("#slide_azi").val( $("#slide_azi").attr("animate_val") );
					CubeControl.update_view(); 
		    }     
      }
		);
}


function animate_spin(delta_radians) {
		// lock the buttons
		if(locked_buttons) return;
		locked_buttons = true;
		CubeControl.ignore_clicks = true;
		

		// do the boogie 
		var azimuth = $("#slide_azi").val()*1.0; // convert from string to number. javascript sucks
		azimuth = azimuth % (100*Math.PI*2);  // Re-center
		$("#slide_azi").attr("animate_val", azimuth); // prep temporary animation variable
		azimuth += delta_radians*100;
		//console.log(azimuth);
		$("#slide_azi").animate( { 
			animate_val: azimuth 
		},{ duration: 2000, 
		    complete: function(){
					locked_buttons = false;
					CubeControl.ignore_clicks = false;
				},
				step: function() {  
					//console.log($("#slide_azi").attr("animate_val") ); 
					$("#slide_azi").val( $("#slide_azi").attr("animate_val") );
					CubeControl.update_view(); 
		    }     
      }
		);
}


var is_spinning = false;
function start_spin( start_spin ){
	  if ( position == 0 ) return;

		// dont spin if there's no menu.
		if( menustate == 0 ) return;

		if( start_spin ){
			if( is_spinning ) return; // cube is already spinning - dont start another thread.
			// otherwise set the state variable and go!
			is_spinning = true;	
	  }

		if( !is_spinning ){
			return;
		}

		var azimuth = $("#slide_azi").val()*1.0; // convert from string to number. javascript sucks
		azimuth += 1 ;
		azimuth = azimuth % (100*Math.PI*2);  // Re-center
		$("#slide_azi").val( azimuth  ); 
		CubeControl.update_view();
		setTimeout("start_spin( false )",25 ) 
}

function stop_spin(){
		is_spinning = false;
}

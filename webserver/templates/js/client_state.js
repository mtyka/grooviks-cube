// client_state.js
// client state manager

var client_state = "IDLE";
var game_state = "UNBOUND";
var active_position = 0;
var locked_buttons=false;
var temp_lock = false;

function on_game_state_change(newState, activePosition, clientstate) {
	//     game_state = newState
	$('#game_state').val( newState )
	$('#active_position').val( activePosition )

	if (temp_lock)
		return;

	active_position = activePosition;
	var old_client_state = client_state;
	new_client_state = clientstate[position-1];
	new_game_state = newState;

	console.log("ActivePlayer: " + active_position + " MyPosition: " + position );
	console.log("Server: NewState: " + new_client_state + " OldState: " + client_state );
	console.log("Server: NewGameState: " + new_game_state + " OldGameState: " + game_state );

	//timeout.reset_timeout();

	var old_game_state = game_state;
	game_state = new_game_state;

	client_state = new_client_state;
	if ( client_state == "IDLE" ){

		goto_idle_screen();
	}
	else{
		if ( client_state == "HOME" ){

			if (global.isKiosk() && global.activePlayers.length >= 0)
				clicked_3player();
			else{	//for web version.
				clicked_alone();
			}
		}
		else {
			if ( client_state == "SING" ){
				if( game_state == "SINGLE_INVITE" ){
					goto_join_screen();
				}
				else
				if( game_state == "SINGLE" ){
					console.log("Deciding on Single player: ActivePlayer: " + active_position + "MyPosition: " + position );
					if ( active_position == position ){
						if( old_game_state != new_game_state ){
							timeout.reset_game_timeout();
						}
						clear_screen();
					}
					else
						goto_queued_screen();
				}
				else{
					if( game_state == "VICTORY" ){

						clear_screen();
					}
				}
			} //close client_state == "SING"
			else {
				if ( client_state == "MULT" ){
					if( game_state == "SINGLE_INVITE" ){

						goto_waiting_screen();
					}
					else {
						if( game_state == "MULTIPLE" ){
							// active player gets to select difficulty mode.
							if ( new_client_state == "MULT" && old_client_state == "HOME" ){
								goto_level_screen();   // create level screen
							}
							else {
								// active player comes from a waiting screen
								if ( new_client_state == "MULT" && old_client_state == "MULT" && old_game_state == "SINGLE_INVITE"  ){
									goto_level_screen();   // create level screen
								}
								else if (old_client_state == "IDLE"){
									goto_join_screen();
								}
							}
						}
						else{
							if( game_state == "VICTORY" ){
								goto_victory_screen();
							}
						}
					}
				} //close client_state == "MULT"
				else {
					if ( client_state == "VICTORY" ){
						//clear_screen();
						goto_victory_screen();
					}
					else
						console.log("Unknown client_state:" + client_state );
				}
			} // close client_state != "SING"
		} // close client_state != "HOME"
	} //close client_state == "IDLE"

	temp_lock = true;
	setTimeout(function(){temp_lock = false;}, 100);
	global.turnCheck();
	CubeControl.update_view();
}

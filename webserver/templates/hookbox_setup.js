
// ####################################################################
// #################### Communications Setup ##########################
// ####################################################################

var hookbox_conn = null;
var subscription = null;


function establish_hookbox_connections() {
    if( !is_hookbox_loaded ) {
        alert("Failed to connect to hookbox server.");
    }

    // create a connection object and setup the basic event callbacks.
    hookbox_conn = hookbox.connect(server);
    //hookbox_conn.onOpen = function() { alert("connection established!"); };
    hookbox_conn.onError = function(err) { alert("Failed to connect to hookbox server: " + err.msg); };

    subscription = null;
    hookbox_conn.onSubscribed = function(channelName, _subscription) {
        if( channelName == 'iframe' ) {
            subscription = _subscription;                
            subscription.onPublish = function(frame) {
                on_message_pushed( frame.payload );
            };  
        }
        if( channelName == 'faceclick' ) {
            faceclick_subscription = _subscription;                
            faceclick_subscription.onPublish = function(frame) {
                playFaceClickSound(frame);
                clog('Heard about click on face ' + frame.payload);
            };  
        }

        if( channelName == 'colorcalibrx') {
            calib_subscription = _subscription;
                calib_subscription.onPublish = function(frame) {
                    clog('Heard calibration message');
                    clog(frame.payload);
                    var rgb_floats = decompress_rgbfloat(frame.payload);
                    
                    changeSlider ( rgb_floats );
                    clog('done with calibration message');
            };
        if( channelName == 'movesfromsolved' ) {
            movesfromsolved_subscription = _subscription;                
            movesfromsolved_subscription.onPublish = function(frame) {
                clog('moves_from_solved has announced answer' + frame.payload);
            		moves_from_solved = frame.payload;
								// start inactivity counter which will trigger the message to appear
								next_flash_moves_display = setTimeout("flash_moves_display()", 5000 ); 
						};  
        }
        if( channelName == 'gameState' ) {
        	gamestate_subscription = _subscription;
            gamestate_subscription.onPublish = function(frame) {
                on_game_state_change(frame.payload["gamestate"], frame.payload["active_position"], frame.payload["clientstate"]);
            };  
        }
        if( channelName == 'rotationStep' ) {
            rotation_subscription = _subscription;
            rotation_subscription.onPublish = function(frame) {
                playRotationSound(frame.payload);
            }
        }
        if( channelName == 'volumeControl' ) {
            vol_subscription = _subscription;
            vol_subscription.onPublish = function(frame) {
                handle_vol(frame.payload);
            }
        }
    };

   // Subscribe to the pubsub channel with the colors
   hookbox_conn.subscribe("iframe");
   hookbox_conn.subscribe("faceclick");
   hookbox_conn.subscribe("movesfromsolved");
   hookbox_conn.subscribe("gamemode");
   hookbox_conn.subscribe("gameState");
   hookbox_conn.subscribe("rotationStep");
   hookbox_conn.subscribe("volumeControl");
   hookbox_conn.subscribe("cubemode");
   hookbox_conn.subscribe("colorcalib");
   hookbox_conn.subscribe("colorcalibrx");
}




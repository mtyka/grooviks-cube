
function get_querystring_parameter(name) {
  var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
  return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

// safe way to log things on webkit and not blow up firefox
function clog(msg) {
    if( window.console ) {
        console.log(msg);
    }
}

// some global url parameters
var position = get_querystring_parameter('position') || null;
var grey = get_querystring_parameter('grey') || 0;

// ####################################################################
// #################### Framerate calculation #########################
// ####################################################################

var HOW_OFTEN_DISPLAY_FRAMERATE = 400;  // ms between updates
var frames_rendered=0;
var frame_cnt_reset_at = (new Date()).getTime(); // epoch time in ms

function display_framerate() {
  var now = (new Date()).getTime();
  var howlong_ms = now - frame_cnt_reset_at;
  var fps = frames_rendered * 1000 / howlong_ms;
  $('#framerate').html( Math.floor(fps*10) / 10 );

  // reset
  frames_rendered = 0;
  frame_cnt_reset_at = now;
}

// ####################################################################
// ###################### jquery helpers ##############################
// ####################################################################


jQuery.fn.elementlocation = function() {
  var curleft = 0;
  var curtop = 0;

  var obj = this;

  do {
    curleft += obj.attr('offsetLeft');
    curtop += obj.attr('offsetTop');

    obj = obj.offsetParent();
  } while ( obj.attr('tagName') != 'BODY' );


  return ( {x:curleft, y:curtop} );
};

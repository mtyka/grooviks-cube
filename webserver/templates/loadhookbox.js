
// load the hookbox library, or display an error
var is_hookbox_loaded = false;

// This code loads the hookbox.js from the current host but changing the port to 2974.
var server = location.protocol + '//' + location.hostname + ':2974';

// Dynamically inserts the code to load the script into the page.


function loadScript(sScriptSrc) {
  var headelem = document.getElementsByTagName('head')[0];
  var oScript = document.createElement('script');
  oScript.type = 'text/javascript';
  oScript.src = sScriptSrc;
  oScript.onload = function() {
    is_hookbox_loaded = true;
    establish_hookbox_connections();
  }
  oScript.onerror = function() {
    alert("Could not load library from hookbox server.");
  }
  headelem.appendChild(oScript);
}
$(document).ready(function() {
    loadScript( server + '/static/hookbox.js' );
    });
</script>
<script type="text/javascript">

function get_querystring_parameter(name) {
  var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
  return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}
// ####################################################################
// ######################## Configuration #############################
// ####################################################################

var HOW_LONG_STABLE_BEFORE_SHOWING_ARROWS = 700;  // ms

var HOW_OFTEN_DISPLAY_FRAMERATE = 400;  // ms between updates
var RENDER_WITH_CANVAS = true;

/* SVG is an alternate way to render. It's not fully hooked up (no arrows, or input)
   but does offer smooth blending between frames using jquery.animate.
   It also renders vector-based when zooming on ipad/iphone although doesn't
   seem to offer real performance benefits on that platform.
 */
var RENDER_WITH_SVG = false;
var SVG_ANIMATION_SPEED = 65;  // how many ms to blend color transitions over

var position = get_querystring_parameter('position') || null;
var grey = get_querystring_parameter('grey') || 0;



// ####################################################################
// #################### Framerate calculation #########################
// ####################################################################

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

$(document).ready(function() {
    setInterval( display_framerate, HOW_OFTEN_DISPLAY_FRAMERATE );
    });



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


var Numpad = (function(){
  var my = {}

  my.number_write = function(x)
  {
    var text_box = document.getElementById("number");
    if(x>=0 && x<=9)
    {
      if(isNaN(text_box.value))
     text_box.value = 0;
   text_box.value = (text_box.value * 10)+x;
    }
  }
  my.number_clear = function()
  {
    document.getElementById("number").value = 0;
  }
  
  my.number_enter = function( action )
  {
    var text_box = document.getElementById("number");
    var num = text_box.value;

    // just to be clear - this is NOT supposed to be a secure lock or anything - 
    // only to prevent anyone without keyboard access from escaping from this page 
    if( num == '761862' ){
      if ( action == "admin" ){
        window.location.assign( "http://" +  window.location.host + "/admin_cube" ) 
      } else 
      if ( action == "reload" ){
        window.location.reload(true);
      }
    }else{
      alert("Code incorrect")
    }
  }

  my.show = function(){
    my.timeout = setTimeout( Numpad.hide,  8000 )
    $("#admin_background").fadeIn()
  }
  
  my.hide = function(){
    clearTimeout( my.timeout )
    $("#admin_background").fadeOut()
  }

  my.timeout = null;

  $( function(){ 
    $("#footer").click(function(){
      Numpad.number_clear()
      Numpad.show()
      });

    $("#admin_background").click(function(){
      Numpad.number_clear()
      Numpad.hide()
      });

    $("#securitycode").click(function(){
      return false; 
      });
  })

  return my;
}())
  

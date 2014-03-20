var clients_seen = [];

function draw_slider(client_num, client_value) {
    var header = 'Player console ' + client_num
    if ( client_num == 0 )
      header = 'Physical Cube (server)'
    var m = '<div class="slidertext" id="slidertext' + client_num + '">' + header + '<div class="slider" id="client' + client_num +'"></div></div><br>';
    var pos = $.inArray(client_num, clients_seen);
    if( clients_seen.length == 1 ) {
        $('#slider-group').append(m);
    } else if ( pos == 0 ) {
        $(m).insertBefore('#slidertext'+clients_seen[pos+1]);
    } else {
        $(m).insertAfter('#slidertext'+clients_seen[pos-1]);
    }
    $( '#client'+client_num ).slider({
        orientation: "horizontal",
        range: "min",
        max: 100,
        min: 0,
        value: client_value,
        slide: publish_volume,
        change: publish_volume,
    });
}

function publish_volume (event, ui) {
    var outgoing = ["update"];
    for(var i=0;i<=clients_seen[clients_seen.length-1];i++){
        if( -1 != $.inArray(i.toString(), clients_seen)) {
            outgoing.push($('#client'+i).slider("option","value"));
        } else {
            outgoing.push(0);
        }
    }
    HookboxConnection.hookbox_conn.publish('volumeControl', outgoing );
    outgoing = [];
}
function update_sliders(position, value) {
    if ( clients_seen.length == 0 ) {
        $( '#slider-group' ).html('');
    }
    if( $.inArray(position, clients_seen) == -1 ) {
        clients_seen.push(position);
        clients_seen.sort();
        draw_slider(position, value);
    } else {
        $("#client"+position).slider("option", "value", value);
    }
}

function ping_client_to_return_volume_level(){
  HookboxConnection.hookbox_conn.publish("volumeControl", ["ping"] )
}

function init_volume_control() {
  // set pong handler to our function that handles such pongs (only part of admin interface)
  
  pong_handler = update_sliders;
  ping_handler = null;

  setInterval(ping_client_to_return_volume_level, 5000);
}


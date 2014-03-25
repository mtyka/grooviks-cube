var clients_seen = [];

function draw_box(client_num, client_value) {
    var parentDiv = 'slidertext';
    var header = 'Player console ' + client_num;
    var submitButton = '<input id="submitButton" type="button" onclick="publish_volume(this.form)" value="submit">';
    if ( client_num == 0 ){
        header = 'Physical Cube (server)';
    }
    var m = '<div class="'+parentDiv+'" id="textBox-' + client_num + '">' + header + '<br><input id="client' + client_num +'" type="text" value="'+ client_value +'"><br>';
    var pos = $.inArray(client_num, clients_seen);

    if( clients_seen.length == 1 ) {
        $('#volumeForm').append(m);
    } 
    else if ( pos == 0 ) {
        $(m).insertBefore('#textBox-'+clients_seen[pos+1]);
    } 
    else {
        $(m).insertAfter('#textBox-'+clients_seen[pos-1]);
    }

    if ($('#submitButton').length == 0)
        $('#volumeForm').append(submitButton);
}

function publish_volume (form) {
    var outgoing = ["update"];
    for(var i = 0; i <= 3; i++){
        if( -1 != $.inArray(i.toString(), clients_seen)) {
            var vol = form['client'+i].value;
            if (parseInt(vol) > 100){
                vol = '100'; 
            }
            else if (parseInt(vol) < 0 || vol == '' || (/_a-zA-Z|\s/g).test(vol)){
                vol = '0';
            }

            outgoing.push(vol);
        } else {
            outgoing.push(0);
        }
    }
    //console.log(outgoing);
    HookboxConnection.hookbox_conn.publish('volumeControl', outgoing );
}
function update_sliders(position, value) {
    if ( clients_seen.length == 0 ) {
        $( '#volumeForm' ).html('');
    }
    if( $.inArray(position, clients_seen) == -1 ) {
        clients_seen.push(position);
        clients_seen.sort();
        draw_box(position, value);
    } else {
        if ( $("#client"+position+':focus').length == 0 )
            $("#client"+position).val(value);
    }
}

function ping_client_to_return_volume_level(){
  HookboxConnection.hookbox_conn.publish("volumeControl", ["ping"] );
}

function init_volume_control() {
  // set pong handler to our function that handles such pongs (only part of admin interface)
  
  pong_handler = update_sliders;
  ping_handler = null;

  setInterval(ping_client_to_return_volume_level, 5000);
}


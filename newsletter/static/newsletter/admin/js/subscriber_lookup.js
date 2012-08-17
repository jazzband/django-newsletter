var JsonSubscribers = {
    init: function(inputname, add) {
        inp = document.getElementById(inputname);
        addEvent(inp, "change", function(e) { JsonSubscribers.setSubscribers(inp.value); });
        if (add==true && inp.value != "") {
            JsonSubscribers.setSubscribers(inp.value);
        }
    },

    setSubscribers: function(id) {
        SelectBox.move_all('id_subscriptions_to', 'id_subscriptions_from');

        if (id) {
            xmlhttp.open( "GET", "/admin/newsletter/message/"+id+"/subscribers/json/", true );
            xmlhttp.onreadystatechange=function() {
                if (xmlhttp.readyState==4 && xmlhttp.status == 200) {

                    objects = eval( "(" + xmlhttp.responseText + ")" );

                    var from_box = document.getElementById('id_subscriptions_from');
                    for (var i = 0; (option = from_box.options[i]); i++) {
                        for (j=0;(object = objects[j]);j++) {
                            if (object.pk.toString() == option.value) {
                                option.selected = true;
                            }
                        }
                    }
                    SelectBox.move('id_subscriptions_from', 'id_subscriptions_to');
                }
            }
            xmlhttp.send(null)
        }
    }
};

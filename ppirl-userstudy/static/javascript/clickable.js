 /*
    Author: Yumei Li
    Date: 12/23/2017
    Requirement: jquery-3.2.1
    This file makes the elements in the file clickable
*/

function get_response(clicked_object) {
    console.log(clicked_object);
    var mode_info = clicked_object.getAttribute("mode");
    var responses = clicked_object.id + "\n" + mode_info;

    return {
        "response": responses
    };
}

       $(function() {
    $('#test_col').bind('click', function() {
        $.getJSON($SCRIPT_ROOT + '/get_cell', get_response(this), function(data) {
        });
        return false;
    });
});

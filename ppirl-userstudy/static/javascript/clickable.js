 /*
    Author: Yumei Li
    Date: 12/23/2017
    Requirement: jquery-3.2.1
    This file makes the elements in the file clickable
*/

function get_response(clicked_object) {
    console.log(clicked_object);
    var mode_info = clicked_object.getAttribute("mode");
    var id1 = clicked_object.children[0].id;
    var id2 = clicked_object.children[2].id;

    return {
        "id1": id1,
        "id2": id2,
        "mode": mode_info
    };
}

$(function() {
    $('.clickable_cell').bind('click', function() {
        var current_cell = this;
        $.getJSON($SCRIPT_ROOT + '/get_cell', get_response(current_cell), function(data) {
            current_cell.children[0].innerHTML = data.value1;
            current_cell.children[2].innerHTML = data.value2;
        });
        return false;
    });
});
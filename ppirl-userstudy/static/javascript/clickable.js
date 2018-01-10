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

function get_cell_ajax(current_cell) {
    $.getJSON($SCRIPT_ROOT + '/get_cell', get_response(current_cell), function(data) {
        if(data.value1 && data.value2 && data.mode) {
            current_cell.children[0].innerHTML = data.value1;
            current_cell.children[2].innerHTML = data.value2;
            current_cell.setAttribute("mode", data.mode);
            if(data.mode == "full") {
                current_cell.classList.remove("clickable_cell");
            }

            var bar_style = 'width:' + data.cdp + '%';
            $("#privacy-budget-bar").attr("style", bar_style);
            $("#privacy-budget-value").html(data.cdp + "%")
        }
    });
}

$(function() {
    $('.clickable_cell').bind('click', function() {
        var current_cell = this;
        if(current_cell.getAttribute("mode") != "full") {
            get_cell_ajax(current_cell);
        }
        return false;
    });

    $('.clickable_big_cell').bind('click', function() {
        var first_name_cell = this.children[0];
        var last_name_cell = this.children[2];
        if(first_name_cell.getAttribute("mode") != "full") {
            get_cell_ajax(first_name_cell);
        }
        if(last_name_cell.getAttribute("mode") != "full") {
            get_cell_ajax(last_name_cell);
        }
        this.classList.remove("clickable_big_cell");
        return false;
    });
});


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
    $.fn.extend({
        animateCss: function (animationName, callback) {
            var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
            this.addClass('animated ' + animationName).one(animationEnd, function() {
                $(this).removeClass('animated ' + animationName);
                if (callback) {
                  callback();
                }
            });
            return this;
        }
    });

    $.getJSON($SCRIPT_ROOT + '/get_cell', get_response(current_cell), function(data) {
        if(data.value1 && data.value2 && data.mode) {
            current_cell.classList.add("animated");
            current_cell.classList.add("fadeIn");
            window.setTimeout( function(){
                current_cell.classList.remove("animated");
                current_cell.classList.remove("fadeIn");
            }, 200);

            current_cell.children[0].innerHTML = data.value1;
            current_cell.children[2].innerHTML = data.value2;
            current_cell.setAttribute("mode", data.mode);
            if(data.mode == "full") {
                current_cell.classList.remove("clickable_cell");
            }
            

            var bar_style = 'width:' + data.cdp + '%';
            $("#character-disclosed-bar").attr("style", bar_style);
            $("#character-disclosed-value").html(data.cdp + "%")

            var bar_style2 = 'width:' + data.KAPR + '%';
            $("#privacy-risk-bar").attr("style", bar_style2);
            $("#privacy-risk-value").html(data.KAPR + "%")
        }
    });
}

$(function() {
    // mark the double missing cell as unclickable
    $('.clickable_cell').each(function() {
        if( this.children[0].innerHTML.indexOf('missing') != -1 && this.children[2].innerHTML.indexOf('missing') != -1 ) {
            this.classList.remove("clickable_cell");
        }
    });

    // bind the clickable cell to ajax openning cell action
    $('.clickable_cell').bind('click', function() {
        var current_cell = this;
        if(current_cell.getAttribute("mode") != "full") {
            get_cell_ajax(current_cell);
        }
        return false;
    });

    // big cell is the name swap cell
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


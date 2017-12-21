/*
    Author: Qinbo Li
    Date: 12/19/2017
    Requirement: jquery-3.2.1
    This file is for practice grading
*/

function get_response() {
    var responses = new Array()
    var i = 0;
    var c = $(".ion-android-radio-button-on").each(function() {
        responses[i] = this.id;
        i += 1;
    });

    return {
        "response": responses.join()
    };
}

$(function() {
    $('#submit_btn').bind('click', function() {
        $.getJSON($SCRIPT_ROOT + $THIS_URL + '/grading', get_response(), function(data) {
            $("#feedback").html(data.result);
            $("#submit_btn").css({"display": "none"});
            $("#next_button_form").css({"display": "inline"})
        });
        return false;
    });
});

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
        $.getJSON($SCRIPT_ROOT + '/practice/full_mode/grading', get_response(), function(data) {
            $("#feedback").innerHTML(data.result);
        });
        return false;
    });
});

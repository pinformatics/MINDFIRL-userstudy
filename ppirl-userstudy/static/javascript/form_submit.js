/*
    Author: Qinbo Li
    Date: 12/22/2017
    Requirement: jquery-3.2.1
    This file is for form submit, and sending user click data
*/

function post(path, params, method) {
    // COPYRIGHT: https://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
    method = method || "post"; // Set method to post by default if not specified.
    var formData = new FormData();
    formData.append("user_data", params);
    var request = new XMLHttpRequest();
    request.open("POST", path);
    request.send(formData);
}

$(function() {
    $('#button_next').bind('click', function() {
        post($SCRIPT_ROOT+'/save_data', $user_data, "post");
        window.location.href = $NEXT_URL;
    });
});

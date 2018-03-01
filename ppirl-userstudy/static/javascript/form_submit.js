/*
    Author: Qinbo Li
    Date: 12/22/2017
    Requirement: jquery-3.2.1, clickable.js
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

function reset_choice_panel() {
    var $options = $("li.input_radio");

    $options.click(function(e){
        e.preventDefault();
        e.stopPropagation();
        $(this).parent().find("li.input_radio").removeClass("ion-android-radio-button-on");
        $(this).parent().find("li.input_radio").addClass("ion-android-radio-button-off");
        $(this).removeClass("ion-android-radio-button-off");
        $(this).addClass("ion-android-radio-button-on");
        var $selected_id = $(this).attr("id");
        var $diff = $(this).parent().parent().find("li.diff");
        var $same = $(this).parent().parent().find("li.same");
        if($selected_id.indexOf("a1") > 0 || $selected_id.indexOf("a2") > 0 || $selected_id.indexOf("a3") > 0) {
            $diff.css("border-color", "#30819c");
            $same.css("border-color", "transparent");
        }
        else {
            $diff.css("border-color", "transparent");
            $same.css("border-color", "#30819c");
        }

        // save the user click data
        $type = "type: answer";
        $this_click = "id: " + $selected_id;
        var dt = new Date();
        $click_time = "time: " + dt.getHours() + "h" + dt.getMinutes() + "m" + dt.getSeconds() + "s";
        $click_timestamp = "timestamp: " + dt.getTime();
        $url = "url: " + $THIS_URL;
        $data = [$type, $this_click, $click_time, $click_timestamp, $url].join()
        $user_data += $data + ";\n";
    });
}

function get_summitted_answers() {
    var c = $(".ion-android-radio-button-on").each(function() {
        $type = "type: final_answer";
        $this_click = "id: " + this.id;
        var dt = new Date();
        $click_time = "time: " + dt.getHours() + "h" + dt.getMinutes() + "m" + dt.getSeconds() + "s";
        $click_timestamp = "timestamp: " + dt.getTime();
        $url = "url: " + $THIS_URL;
        $data = [$type, $this_click, $click_time, $click_timestamp, $url].join()
        $user_data += $data + ";\n";
    });
}

/* 
    This function defines the behavior of the next button 
    1. post the user click data to server.
    2. relocate to the next page.
*/
$(function() {
    $('#button_next').bind('click', function() {
        $('#button_next').attr("disabled", "disabled");
        
        // save this click data
        $type = "type: jumping";
        var dt = new Date();
        $click_time = "time: " + dt.getHours() + "h" + dt.getMinutes() + "m" + dt.getSeconds() + "s";
        $click_timestamp = "timestamp: " + dt.getTime();
        $url = "url: " + $THIS_URL;
        $data = [$type, $click_time, $click_timestamp, $url].join()
        $user_data += $data + ";\n";

        get_summitted_answers();
        post($SCRIPT_ROOT+'/save_data', $user_data, "post");
        $user_data = "";

        $(window).off("beforeunload");
        window.location.href = $NEXT_URL;
    });
});


function all_questions_answered() {
    var i = 0;
    var c = $(".ion-android-radio-button-on").each(function() {
        i += 1;
    });
    return true; // disable this feature for dev.
    // return (i == 6);
}

/*
    This function defines the behavior of the next button in record linkage page:
    1. disable this button
    2. post the user data to server
    3. use ajax to load the next page of data (if any)
    4. if the next page is the last page, change this button to normal next button
    5. enable the button
*/
$(function() {
    $('#button_next_rl').bind('click', function() {
        if( !all_questions_answered() ) {
            alert("Please answer all questions to continue.");
        }
        else {
            // save this click data
            $type = "type: moving";
            var dt = new Date();
            $click_time = "time: " + dt.getHours() + "h" + dt.getMinutes() + "m" + dt.getSeconds() + "s";
            $click_timestamp = "timestamp: " + dt.getTime();
            $url = "url: " + $THIS_URL;
            $data = [$type, $click_time, $click_timestamp, $url].join()
            $user_data += $data + ";\n";

            $('#button_next_rl').attr("disabled", "disabled");
            get_summitted_answers();
            post($SCRIPT_ROOT+'/save_data', $user_data, "post");
            $user_data = "";
            $.ajax({
                url: $SCRIPT_ROOT + $THIS_URL + '/next',
                data: {},
                error: function() {},
                dataType: 'json',
                success: function(data) {
                    // update delta
                    $DELTA = data['delta'];
                    // update table content
                    $("#table_content").html(data['page_content']);
                    // update page number
                    $("#page-number").html(data['page_number']);
                    make_cell_clickable();
                    refresh_delta();
                    reset_choice_panel();
                    if(data['is_last_page'] == 0) {
                        $('#button_next_rl').attr("disabled", false);
                    }
                    else {
                        $('#button_next_rl').css("display", "none");
                        $('#button_next').css("display", "inline");
                    }
                },
                type: 'GET'
            });
        }
        return false;
    });
});

/*
    Author: Qinbo Li
    Date: 10/19/2017
    Requirement: jquery-3.2.1
    This file defines the behavior of the instr
*/

$(document).ready(function(){
    $('#checkbox_0').change(function() {
        if($(this).is(":checked")) {
            $('#button_0').attr("disabled", false);
            $('.checkboxP').find('label').css("background", "#30819C")
        }
        else {
            $('#button_0').attr("disabled", "disabled");
            $('.checkboxP').find('label').css("background", "#eee")
        }
    });
});

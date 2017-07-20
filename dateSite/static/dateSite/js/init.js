//Show email confirmation message if user hasn't your email verified
var credits, verify;
$(document).ready(function() {
    s3 = $("#s3").val();
    s3_root = $("#s3_root").val();
    var client = $("#is_client").val();
    var i_feel = s3 + "dateSite/img/icons/" + $("#feel").val();
    credits = $("#credits").val();
    verify = $("#verified").val();

    if(client == 'True'){
        if(verify == 'False')
            $('#verifiedModal').modal('show');
    }

    $('#feel-icon').attr('src', i_feel);
    $("#credits_billing").text(credits);
});

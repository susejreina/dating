$(document).ready(function() {
    s3 = $("#s3").val();
    s3_root = $("#s3_root").val();
    $('#signupModal').modal('hide');
    if ($("#ids").val() != "0") {
        scrollActivity();
    }
    hyperLinks();
});

function hyperLinks() {
    $("#members-content").on("click", ".btn-inbox", function() {
        $("#signupModal").modal('show');
    });
    $("#members-content").on("click", ".action-icons", function() {
        $("#signupModal").modal('show');
    });
    $("#members-content").on("click", ".pic-profile", function() {
        $("#signupModal").modal('show');
    });
    $("#members-content").on("click", ".item-preview", function() {
        $("#signupModal").modal('show');
    });
}

$(document).ready(function() {
    if ($("#ids").val() != "0") {
        scrollActivity();
    }
    hyperLinks();
    pic_width = $('#profile-pic-container').parent().width();
    $('#profile-pic-container').height(pic_width);
    $('#profile-pic-container').width(pic_width);
    $('.alert-pic-preview').height($('.alert-pic-preview>img').width());
    $(".item-preview").click(function(e) {
        album_id = $(e.target).data("albumid");
        profile = "/" + $(e.target).data("username");
        localStorage.setItem('albumid', album_id);
        window.location.replace(profile);
    });

});

function hyperLinks() {
    //Link to profile view
    $("#members-content").on("click", ".member-main-picture", function() {
        linkToProfile($(this));
    });
    $("#members-content").on("click", ".gallery-preview>.column", function() {
        linkToProfile($(this));
    });
    $("#members-content").on("click", ".profile-info>div>strong>b", function() {
        linkToProfile($(this));
    });
    //Link to inbox view
    $("#members-content").on("click", ".btn-inbox", function() {
        var user = $(this).parents("div[name=list_members]").attr("data-username");
        document.location.href = "/inbox/" + user;
    });
}

function linkToProfile(obj) {
    var user = $(obj).parents("div[name=list_members]").attr("data-username");
    document.location.href = "/" + user;
}

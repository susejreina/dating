$(document).ready(function() {
    chatHyperLinks();
});

function chatHyperLinks() {
    //Link to profile view
    $(".chat").on("click", "li:not(.notchatlist)", function() {
        linkToProfile($(this));
    });
}

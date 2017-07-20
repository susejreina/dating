$(document).ready(function() {
    eventsMnu();
    showBadgets();
    $(".logo").on("click", function() {
        location.href = '/';
    })
    $(".action-area").on('click', '.upgradePremiumModal', function(){ $('#upgradePremiumModal').show(); });
    $(".feeling-list").on("click", "li", changeFeeling);
});

function showBadgets() {
    $(".badget").each(function() {
        if (parseInt($(this).text()) > 0) {
            $(this).show();
        }
    });
}

function eventsMnu() {
    $(".mnu > li").on("click", manageWindow);
}

function manageWindow() {
    objMnu = $(this);
    disMnu = objMnu.attr("class").split("-")[1];
    let qty = $("div[name=mnu-window]:visible").length;
    if (qty > 0) {
        itsme = false;
        $("div[name=mnu-window]:visible").each(function() {
            let mnu = $(this).attr("class").split("-")[1];
            closeMnuWindow($(this));
            if (disMnu == mnu) {
                itsme = true;
            }
        });
        if (!itsme) { //Close currrent mnu
            openMnuWindow(objMnu);
        }
    } else {
        openMnuWindow($(this));
    }
}

function openMnuWindow(obj) {
    let mnu = obj.attr("class").split("-")[1];
    let positionLeft = 0;
    switch (mnu) {
        case 'search':
            positionLeft = parseInt(obj.offset().left) - (parseInt($(`.win-${mnu}`).outerWidth()) - parseInt(obj.width()));
            $(`.win-${mnu}`).offset({
                left: positionLeft
            }).show();
            break;
        case 'feel':
            positionLeft = parseInt(obj.offset().left) - (parseInt($(`.win-${mnu}`).outerWidth()) - parseInt(obj.width()));
            $(`.win-${mnu}`).offset({
                left: positionLeft
            }).show();
            break;
        case 'alert':
            positionLeft = parseInt(obj.offset().left) - (parseInt($(`.win-${mnu}`).outerWidth()) - parseInt(obj.width()));
            $(`.win-${mnu}`).offset({
                left: positionLeft
            }).show();
            break;
        case 'profile':
            positionLeft = parseInt(obj.offset().left) - (parseInt($(`.win-${mnu}`).outerWidth()) - parseInt(obj.width()));
            $(`.win-${mnu}`).offset({
                left: positionLeft
            }).show();
            break;
        default:
    }
}

function closeMnuWindow(obj) {
    let mnu = obj.attr("class").split("-")[1];
    switch (mnu) {
        case 'search':
            $(`.win-${mnu}`).offset({
                left: 0
            }).hide();
            break;
        case 'feel':
            $(`.win-${mnu}`).offset({
                left: 0
            }).hide();
            break;
        case 'alert':
            $(`.win-${mnu}`).offset({
                left: 0
            }).hide();
            break;
        case 'profile':
            $(`.win-${mnu}`).offset({
                left: 0
            }).hide();
            break;
    }
}

function changeFeeling(){
    let code = $(this).data("code");
    $.ajax({
        type: 'POST',
        url: "/ajax/feeling/",
        data: {
            'feeling': code,
        },
        dataType: "json",
        success: function(data) {
            if (data.error != null) {
                $('#verifiedModal').modal('show');
            } else {
                var img_path = $("#s3").val() + 'dateSite/img/icons/' + data;
                $('#feel-icon').attr('src', img_path);
                closeMnuWindow($(".win-feel"));
            }
        }
    });
}

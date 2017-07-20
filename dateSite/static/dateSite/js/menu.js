$(document).ready(function() {
    $("#buycreditsModal").modal('hide');
    if ($("#show_promo_10").val()=="1"){
        showModalByCredits();
    }

    $("#buyCredits,#retry_pay,#promotions").on('click', showModalByCredits);
    $(".subpage").on("click","[name=openbuycredits]",showModalByCredits);

    var quan = $("#alertsquantity").text();
    if (quan > 0) {
        $("#alertsquantity").show();
    } else {
        $("#alertsquantity").hide();
    }

    quan = $("#count_inbox").text();
    if (quan > 0) {
        $("#count_inbox").show();
    } else {
        $("#count_inbox").hide();
    }

    //Colocando los valores en la busqueda
    if ($("#minage").val() != 0) {
        $('#id_seaminage').val($("#minage").val());
    }
    if ($("#maxage").val() != 0) {
        $('#id_seamaxage').val($("#maxage").val());
    }
    if ($("#coucode").val() != 0) {
        $('#id_seacountry').val($("#coucode").val());
    }

    //Eventos
    $("#feeling").submit(function() {
        return false;
    });
    $(".btn-feel").click(function() {
        processFeeling($(this));
    });

    $(window).trigger('resize');

    $("#div_id_seaminage").change(function() {
        $('#search-error').empty();
    });
    $("#div_id_seamaxage").change(function() {
        $('#search-error').empty();
    });
    $("#div_id_seacountry").change(function() {
        $('#search-error').empty();
    });

    //Modal instead of Dropdown
    if ($(window).width() <= 576) {
        $(".dropdown-menu").remove();
        $('#menu-search').click(function() {
            $("#modal-search").modal('show');
        });
        $('#menu-feelings').click(function() {
            $("#modal-feelings").modal('show');
        });
        $('#menu-alerts').click(function() {
            updateAlerts();
            $("#alertsquantity").text(0).hide();
            $("#modal-alerts").modal('show');
        });
        $('#menu-profile').click(function() {
            $("#modal-profile").modal('show');
        });
    } else {
        $('#menu-alerts').click(function() {
            updateAlerts();
            $("#alertsquantity").text(0).hide();
        });
    }

    //Avoid dropdown closing when clicked
    $('.span-search').on('click', function(event) {
        $('.dropdown-profile-menu').parent().removeClass('open');
        $('.dropdown-search-menu').parent().toggleClass('open');
    });
    $('.span-profile').on('click', function(event) {
        $('.dropdown-search-menu').parent().removeClass('open');
        $('.dropdown-profile-menu').parent().toggleClass('open');
    });

    //close dropdown when user click outsite
    $('body').on('click', function(e) {
        if (!$('.span-search').is(e.target) &&
            $('.span-search').has(e.target).length === 0 &&
            $('.open').has(e.target).length === 0
        ) {
            $('.btn-group').removeClass('open');
        }
    });

    if (window.location.pathname == "/") {
        $("#search").submit(function() {
            return false;
        });
        $('.search-btn').on('click', simple_search);
    }

    initUploadFieldMenu();
});

function showModalByCredits() {
    $("#messageModal").modal('hide');
    $("#buycreditsModal").modal('show');
    $('#chatform').popover('dispose');
}

function closeModalByCredits() {
    $("#buycreditsModal").modal('close');
}

function processFeeling(obj) {
    var feeling = obj.val();
    var sender = 0;
    if ($("#sender").length > 0) {
        sender = $("#sender").val();
    }
    $.ajax({
        type: 'POST',
        url: "/ajax/feeling/",
        data: {
            'feeling': feeling,
            'sender': sender,
        },
        dataType: "json",
        success: function(data) {
            if (data.error != null) {
                $('#verifiedModal').modal('show');
            } else {
                var img_path = $("#s3").val() + 'dateSite/img/icons/' + data;
                $('#feel-icon').attr('src', img_path);
            }
        }
    });
}
//Open advanced search
function advanced_search(divId) {
    $("#" + divId).toggle();
}

function updateAlerts() {
    $.ajax({
        url: '/ajax/update/noti/',
        dataType: 'json',
        type: 'POST',
        data: {
            'quantity': 5
        },
        success: function(data) {
            if (data['error'] == 'yes') {
                alert(data["description"]);
            }
        }
    });
}
//load items for pagination calling ajax function
//Do the search
function simple_search() {
    $("#nomoreresults").remove();
    var clase = $('div[name=list_members]').first().attr('class');
    $("#ids").val("");
    $("#members-content").empty();
    getListMoreClients(clase);
}

function initUploadFieldMenu() {
    initUploadFields($('#update-profile-menu'), {
        validation: {
            allowedExtensions: ['jpg', 'png', 'jpeg'],
            sizeLimit: 3000000,
            minSizeLimit: 0,
            itemLimit: 1,
            stopOnFirstInvalidFile: true,
            acceptFiles: false,
            image: {
                maxHeight: 0,
                maxWidth: 0,
                minHeight: 0,
                minWidth: 0
            }
        },
        callbacks: {
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            },
            onComplete: function(id, name, responseJSON, maybeXhr) {
                old_path = $('#dropmenu-profile-pic').attr('src');
                $('#profile-pic-container').find('.img-thumb').attr('src', $('#update-profile-menu').find('img').attr('src'));
                $('#update-profile-menu').hide();
                $('.save-img').css('z-index', '101');
                $('.save-img').show();
                $('.save-img').click(function() {
                    save_menu_pic(responseJSON.filename, old_path);
                });
            },
        },
    });
}

function save_menu_pic(picture, path) {
    $.ajax({
        type: 'POST',
        url: "/ajax/save/uploadedpicture",
        data: {
            'picture': picture,
        },
        success: function(data) {
            if (!data.success) {
                msg = "The picture cannot be upload <br />" + data.error_message;
                show_message(msg);
                $('#picture-preview').attr('src', path);
            } else {
                $('.save-img').css('z-index', '99');
                $('.save-img').hide();
                $('#update-profile-menu').show();
                $('.profile-picture > img').attr('src', data.picpath);
            }
        },
    });
    initUploadFieldMenu();
}

function show_message(message) {
    $('.message-title').html('Warning');
    $('#display-msg').html('<label>' + message + '</label>');
    $('#messageModal').modal('show');
}

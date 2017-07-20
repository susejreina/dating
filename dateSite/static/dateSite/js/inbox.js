$(document).ready(function() {
    //Evento para abrir un correo desde la bandeja de entrada
    $(".contenedor-inbox").on("click", "li[name=items-list-mail]",readMessage);

    $(".list-mails").on("click", "#back", showNotReadMessage);
    if ($("input[name=view_inbox]").length > 0) {
        $("input[name=view_inbox]").on("click", readMessage);
    }
    //Viene de darle al inbox de una chica
    if ($("#id_to").length > 0) {
        let id = $("#id_to").val() + ",";
        let user = $("#user_to").val() + ",";
        composeInbox(id, user);
    }

    $("#input_inbox").on("click focus", cleanInbox);
    $("#input_inbox").on("blur", putInbox);
    $("#recipientsModal").on("click", "#btn-next", function() {
        var recipients = $("input[name=check]:checked").length;
        if (recipients <= 0) {
            $(".recip_msg").show();
        } else {
            recipients = "";
            description = "";
            $("input[name=check]:checked").each(function() {
                var id = $(this).attr("id").split("_")[1];
                recipients += id + ",";
                description += $("#profile_" + id + ">.profile-info>a").text() + ",";
            });
            composeInbox(recipients, description);
        }
    });
    pictures_to_upload = false;
    initUploadInboxPics();
    $("#new_mail").on("click", lookClientInbox);
    $("#send_mail").on("click", prepareSendInbox);
    $(".modal").on("click", '.close', closeModal);
    $(".inb_picture").on('click', '#close_big_picture', closeBigPicture);
    $(".show-current-msg").on("click", ".thumb", seePicture);
});

function readMessage() {
    var id = $(this).attr("data-code");
    var name = $(this).attr("name");
    var orig = $(this).attr("data-origin");
    $.ajax({
        url: '/ajax/get/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'inbcode': id
        },
        success: function(inbox) {
            if (typeof(inbox.error) != "undefined") {
                msg = inbox.error;
                show_message(msg);
            } else {
                $(`.ul-sugges-notread>li input[data-code=${id}]`).parents('li').remove();
                $(".list-sugges-mails").hide();
                $(".list-sugges-notread").hide();
                $(".show-current-msg").show();
                $("div.show-current-msg").html(drawMessage(inbox));
                $(".list-sugges-chats").hide();
                if (name == "view_inbox") {
                    $(`.clientsmyinbox>[data-code=${orig}]`).removeClass().addClass("current_inbox");
                } else {
                    $(`.clientsmyinbox>[data-code=${id}]`).removeClass().addClass("current_inbox");
                }
            }
        }
    });
}

function drawMessage(i) {
    let clicode = $("#sender").val();
    if (clicode == i.codesent) {
        var user = i.userrecieve,
            age = i.agerecieve;
        var pic = ((i.picturerecieve == null) ? `${s3}dateSite/img/default_profile.png` : i.picturerecieve);
    } else {
        var user = i.usersent,
            age = i.agesent;
        var pic = ((i.picturesent == null) ? `${s3}dateSite/img/default_profile.png` : i.picturesent);
    }
    let openMsg = '<div id="msg-reading" class="msg-reading">';
    //INBOX HEADER
    openMsg += '<div class="inb-header">';
    if (i.codeorigin != null) {
        origen = i.codeorigin;
        openMsg += `<div class="btn-history" data-code="${i.codeorigin}">HISTORY</div>`;
    } else {
        origen = i.code;
    }
    openMsg += '<div class="inb-picture">';
    openMsg += `<img src="${pic}" alt="${user}" title="${user}" />`;
    openMsg += '</div>';
    openMsg += '<div class="inb-info-left">';
    if (age == 0) {
        openMsg += `<p class="inb-username">@${user}</p>`;
    } else {
        openMsg += `<p class="inb-username">@${user}, ${age}</p>`;
    }
    openMsg += `<p class="inb-title">${i.title}</p>`;
    openMsg += '</div>';
    openMsg += '<div class="inb-info-right">';
    openMsg += `<p class="inb-date">${i.sentdate}</p>`;
    openMsg += '<input type="button" id="back" name="back" class="btn-inb-back" value="BACK" />'
    openMsg += '</div></div>';
    //INBOX CONTENT
    openMsg += `<div class="inb-content">${i.message}</div>`;
    //INBOX FOOTER
    openMsg += '<div class="inb-footer">';
    openMsg += '<div class="">';
    if (i.pictures != null) {
        openMsg += '<ul class="pictures_mail">';
        for (picture in i.pictures) {
            openMsg += '<li>';
            openMsg += `<img src="${i.pictures[picture]}" class="thumb"/>`;
            openMsg += '</li>';
        }
        openMsg += '</ul>';
    }
    openMsg += '</div>';
    openMsg += '<div class="">';
    openMsg += `<input type="button" value="REPLY" class="reply-inbox" name="reply" id="reply_${i.codesent}" onclick="composeInbox('${i.codesent},', '@${user},', '${origen}', '${i.title}')">`;
    openMsg += '</div>';
    openMsg += '</div>';
    return openMsg;
}

function showNotReadMessage() {
    $("#msg-reading").remove();
    if ($(".ul-sugges-notread>li").length > 0) {
        $(".ul-sugges-notread").show();
        if ($(".ul-sugges-notread>li").length < 3) {
            $(".list-sugges-chats").show();
        }
        markAsReadMessage();
    } else {
        location.reload();
    }
}

function markAsReadMessage() {
    $(".clientsmyinbox>li.current_inbox img.sobre").attr({
        "src": s3 + "dateSite/img/gris_02.png",
        "alt": "Message read"
    });
    $(".clientsmyinbox>li.current_inbox").removeClass().addClass("read");
}

function lookClientInbox() {
    $.ajax({
        url: '/ajax/clients/',
        dataType: 'json',
        type: 'POST',
        success: function(json_members) {
            if (json_members['error'] != null) {
                if (!json_members['error']) {
                    $("#mis-contactos").append(json_members['description']);
                } else {
                    $("#mis-contactos").append(json_members['error']);
                }
            } else {
                drawClient(json_members);
            }
            $('#recipientsModal').show();
        }
    });
}

function drawClient(json_members) {
    $("#mis-contactos").html("");
    client_list = JSON.parse(json_members["members"]);
    for (var member in client_list) {
        var id = client_list[member].fields.pk;
        var current = client_list[member].fields;
        html = '<div id="profile_' + id + '" class="profile-preview">';
        html += '<div class="top-row"><div class="select">';
        html += '<input type="checkbox" class="checkbox check-mark" id="check_' + id + '" name="check" />';
        html += '<label for="check_' + id + '"><span></span></label></div>';
        html += '<div class="profile-member">'
        if (current.profile_picture != null) {
            html += '<img class="pic-profile" src="' + current.profile_picture + '" alt="' + current.cliusername + '" title="' + current.cliusername + '" />';
        } else {
            html += '<img class="pic-profile" src="' + s3 + 'dateSite/img/default_profile.png" alt="' + current.cliusername + '" title="' + current.cliusername + '" />';
        }
        html += '</div></div><div class="profile-info">';
        html += '<a href="/' + current.cliusername + '">@' + current.cliusername + '</a></div></div></div>';
        $("#mis-contactos").append(html);
    }
}

function hideThumbPreview() {
    var count = $('.qq-upload-delete').length;
    if (count <= 1) {
        $('.send-img-preview').hide("slow");
    }
}

function show_message(message) {
    $('.message-title').html('Warning');
    $('#display-msg').html('<label>' + message + '</label>');
    $('#msgModal').show();
}

function initUploadInboxPics() {
    initUploadFields($('#sendpic-form'), {
        disableCancelForFormUploads: true,
        validation: {
            sizeLimit: 5000000,
            itemLimit: 5,
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
            onComplete: function(id, name, responseJSON, maybeXhr) {
                pictures_to_upload = true;
                $('.send-img-preview').show();
            },
            onAllComplete: function(successful, failed) {
                $('#thumbsPreview').append($('#sendpic-form').find('ul'));
                $('#thumbsPreview').append('<div class="info-warnings">Pictures will send when you click on send mail.</div>');
            },
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            },
            onDelete: function(id) {
                hideThumbPreview();
            },
        },
    });
}

function composeInbox(recipients, description, origin, title) {
    $('#recipientsModal').hide();
    $('#writeInboxModal').show();
    $("#recipient_description").val(description.substring(0, description.length - 1));
    $("#recieved_mail").val(recipients.substring(0, recipients.length - 1));
    if (title) {
        $("#subject").val(title);
    } else {
        $("#subject").val("");
    }
    if (origin) {
        $('#inbcodeorigin').val(origin);
    } else {
        $('#inbcodeorigin').val(0);
    }
    $("#input_inbox").html("");
}

function prepareSendInbox() {
    var reciever = $("#recieved_mail").val();
    var sender = $("#sender").val();
    var msg = $.trim($("#input_inbox").text());
    var title = $("#subject").val();
    var origin = $("#inbcodeorigin").val();
    if (msg == "Type your message") {
        msg = "";
    }
    if (title == "") {
        $("#input_inbox").addClass("input_error").text("Write a subject for your message");
    } else if (msg == "") {
        $("#input_inbox").addClass("input_error").text("Write your message to send");
    } else {
        sendInbox(sender, reciever, origin, msg, title);
    }
}

function sendInbox(sender, reciever, origin, msg, title) {
    var form_id = $("#sendpic-form > #id_form_id").val();
    $('#loading-image').show();
    $.ajax({
        url: '/ajax/send/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'recieved': reciever,
            'origin': origin,
            'msg': msg,
            'title': title,
            'form_id': form_id,
        },
        success: function(data) {
            $('#loading-image').hide();
            if (!data.success) {
                msg = data.error_message + '<br />Would you like to buy some? <a data-toggle="modal" data-target="#upgradePremiumModal">Click here</a>';
                show_message(msg);
            } else {
                $('#writeInboxModal').hide();
                pictures_to_upload = false;
                initUploadInboxPics();
                getListInbox();
                $('#thumbsPreview').empty();
                $('.send-img-preview').hide();
                $("#subject").val("");
                $("#input_inbox").text("Type your message");
            }
        }
    });
}

function putInbox() {
    var text = $.trim($(this).text());
    $(this).css({
        'color': '#C0C0C0'
    });
    if (text == "") {
        $(this).html("Type your message");
    }
}

function cleanInbox() {
    var text = $.trim($(this).text());
    $(this).css({
        'color': '#000'
    });
    if (text == "Type your message" || $(this).hasClass("input_error")) {
        $(this).html("");
        $(this).removeClass("input_error");
    }
}

function getListInbox() {
    $.ajax({
        url: '/ajax/list/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'girl': $("#sender").val()
        },
        success: function(data) {
            let lista = `<ul class="clientsmyinbox">`;
            for (i = 0; i < data.length; i++) {
                lista += `<li name="items-list-mail" data-code="${data[i]["inbcode"]}">`;
                lista += `<div class="block-identity">`;
                if (data[i]["profile_picture"]) {
                    lista += `<img class="itemimage" src="${data[i]["profile_picture"]}" alt="@${data[i]["cliusername"]}">`;
                } else {
                    lista += `<img class="itemimage" src="${s3}dateSite/img/default_profile.png" alt="@${data[i]["cliusername"]}">`;
                }
                lista += `</div>`;
                lista += `<div class="info-message">`;
                lista += `<span class="itemname">`;
                if (data[i]["age"] != 0) {
                    if (data[i]["cliusername"].length < 10) {
                        lista += `@${data[i]["cliusername"]}, ${data[i]["age"]}`;
                    } else {
                        lista += `@${data[i]["cliusername"]}`;
                    }
                } else {
                    lista += `@${data[i]["cliusername"]}`;
                }
                lista += `</span>`;
                if (data[i]["cliname"]) {
                    lista += `<span class="itemmessage">${data[i]["cliname"]}</span>`;
                }
                lista += `<span class="itemtitle">${data[i]["short_title"]}</span>`;
                lista += `</div>`;
                lista += `<div class="tips-message">`;
                lista += `<span class="tipdate">${data[i]["formatted_short_inbsenddate"]}</span>`;
                lista += `<span class="tipstatus">`;
                lista += data[i]["status"];
                lista += `</span>`;
                if (data[i]["inbread"]) {
                    lista += `<img class="sobre" src="${s3}dateSite/img/gris_02.png" alt="Message read">`;
                } else {
                    lista += `<img class="sobre" src="${s3}dateSite/img/gris_01.png" alt="Message not read">`;
                }
                lista += `</div>`;
                lista += `</li>`;
            }
            lista += `</ul>`;
            $(".contenedor-inbox").html(lista);
        }
    });
}

function closeModal() {
    $(this).parents(".modal").hide();
}

function seePicture() {
    obj = $(this);
    var src = obj.attr("src");
    img_size(src);
    $("#big_picture").attr("src", src);
    $("#inb_picture").show();
}

function img_size(src) {
    var img = new Image();
    img.onload = function() {
        var width = this.width;
        var height = this.height;
        if (height > width && height > window.innerHeight) {
            var percentage = window.innerHeight * 90 / height / 100;
            width = width * percentage;
        } else if (width > height && width > window.innerWidth) {
            var percentage = window.innerWidth * 90 / width / 100;
            height = height * percentage;
        }
        else if (width == height && width > window.innerWidth){
            var percentage = window.innerHeight * 90 / height / 100;
            height = height * percentage;
            width = height;
        }
        else if (width == height && height > window.innerHeight){
            var percentage = window.innerHeight * 90 / height / 100;
            width = width * percentage;
            height = width;
        }
        else{
            width = width * 0.9;
            height = height * 0.9;
        }
        $('.image-container').height(height);
        $('.image-container').width(width);
    }
    img.src = src;
}

function closeBigPicture() {
    $("#pic-desc").hide();
    $("#inb_picture").hide();
}

$(document).mouseup(function(e) {
    var container = $(".image-container, .close_button");
    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0) {
        closeBigPicture();
    }
});

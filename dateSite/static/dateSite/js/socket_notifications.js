$(document).ready(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + ":5000/ws/");
    //Cuando se recibe un mensaje del servidor
    chatsock.onmessage = function(message) {
        let data = JSON.parse(message.data);
        let objerror = data.error;
        let type = objerror.type;
        switch (type) {
            case "0": //Se recibio msg
                var msg = data.mensaje;
                var sen = data.clientesen;
                var rec = data.clienterec;
                if($(".speech-suggestion").is(":visible")){
                    $(".speech-suggestion").hide();
                }
                evaluateMessage(sen, rec, msg.mescontent, msg.mescontentshort, msg.mescode);
                hasScrollBar("#chat-messages");
                break;
            case "1": //No hay creditos
                showModal(objerror.title,objerror.message,"",true,false);
                $("#message").attr("contentEditable", false);
                $("#send-message").removeClass("input-button").addClass("input-button-disable").off("click");
                break;
            case "2": //El que recibe el chat no esta conectado
                var msg = data.mensaje;
                var sen = data.clientesen;
                var rec = data.clienterec;
                if($(".speech-suggestion").is(":visible")){
                    $(".speech-suggestion").hide();
                }
                showModal(objerror.title,objerror.message,"",true,false);
                evaluateMessage(sen, rec, msg.mescontent, msg.mescontentshort, msg.mescode);
                break;
            case "3": //Alguien vio el profile
                let quantity = parseInt($("#alert").val()) + 1;
                $("#alert").val(quantity);
                quantity = (quantity>9)?"+9":quantity;
                $("#alertsquantity").text(quantity).show();
                /*
                var msg = data.notification;
                var alerts = $("#notifications");
                var ele = $('<div class="notification row"></div>');
                ele.append($('<div class="col-xs-3"></div>').html('<img src="' + msg.clientpicture + '">'));
                ele.append($('<div class="col-xs-9 description">').html('@' + msg.ntymessage + '<span class="date">' + msg.ntydate + '</span>'));
                alerts.prepend(ele);*/
                break;
            case "4"://Alguien envio un correo

                break;
            default:
        }
    };
});

function evaluateMessage(sender, reciever, message, messageshort, mescode) {
    //Le estan escribiendo al cliente
    if (parseInt(sender.clicode) != parseInt($('#sender').val())) {
        inMychats = inList(".clientsmychat>li", sender.clicode, messageshort);
        if (inMychats == false) {
            var inMyrequest = inList(".clientsrequest>li", sender.clicode, messageshort);
            if (inMyrequest === false) {
                updateClientList(".clientsrequest", sender, messageshort);
            }
        }
    }
    else{ //Lo escribio el cliente
        //Busco si esta en mychatsvar
        inMychats = inList(".clientsmychat>li", reciever.clicode, messageshort);
        //Si esta en my chats,en la misma funcion ya se actualizo bagdet y message
        //Si no esta
        if (inMychats == false) {
            //Agregamos el elemento a my chat
            updateClientList(".clientsmychat", reciever, messageshort);
            //Lo buscamos en my request y si existe lo borramos
            if($(`.clientsrequest>li#client_${reciever.clicode}`).length>0){
                $(`.clientsrequest>li#client_${reciever.clicode}`).remove();
            }
            //Si la lista se quedo sin elementos, le colocamos que no hay
            if ($(".clientsrequest>li").length <= 0) {
                $(".clientsrequest").append('<li class="notchatlist">&nbsp;</li>');
            }
        }
    }
    if ($(".chat-form").length>0){ //Estamos en la pantalla de profile
        //Si lo esta escribiendo el cliente
        let sender_sender = (parseInt(sender.clicode) == parseInt($("#sender").val())?true:false);
        let reciever_reciever = (parseInt(reciever.clicode) == parseInt($("#reciever").val())?true:false);
        let sender_reciever = (parseInt(sender.clicode) == parseInt($("#reciever").val())?true:false);
        let reciever_sender = (parseInt(reciever.clicode) == parseInt($("#sender").val())?true:false);
        if ((sender_sender & reciever_reciever) | (sender_reciever & reciever_sender)){ //Si el mensaje es del chat abierto
            addMessage(sender.clicode, message);
            if (sender_reciever & reciever_sender){
                checkReadMessage(mescode);
            }
        }
    }
}

function updateQtyInbox(changer, literal) {
    //changer is the number to increase/decrease the current inbox quantity
    //literal is if the changer is a modifier or is a literal number
    if (literal == true) {
        var qT = changer;
    } else {
        var qT = parseInt($("#count_inbox").text());
        qT = eval(qT + changer);
    }
    if (qT <= 0) {
        $("#count_inbox").text(0).hide();
    } else {
        $("#count_inbox").text(qT).show();
    }
}

function hasScrollBar(element) {
    var obj1 = $(element);
    if (obj1.prop('scrollHeight') > obj1.height()) {
        var scroll = obj1.prop('scrollHeight') - obj1.outerHeight();
        obj1.animate({
            scrollTop: scroll
        }, '500', 'swing');
    }
    return;
}

function checkReadMessage(code) {
    $.ajax({
        url: '/ajax/checkReadMessage/',
        dataType: 'json',
        type: 'POST',
        data: {
            'code': code
        }
    });
}

function updateClientList(lista, client, messageshort) {
    if ($(`${lista}>li.notchatlist`).length > 0) {
        $(`${lista}>li.notchatlist`).remove();
    }
    let code = client.clicode;
    let user = client.cliusername;
    $(lista).prepend($(`<li id="client_${code}" data-username="${user}"></li>`));
    var chat = $(`${lista}>li#client_${code}`);
    var col1 = $('<div class="block-identity"></div>');
    var col2 = $('<div class="block-message"></div>');
    pic = client.clipicture;
    if (pic != null) {
        var pic = pic.replace("/media/", "");
        col1.append($(`<div class="chat-img-container"><img src="${s3_root}${pic}" class="itemimage" alt="${user}"></div>`));
    } else {
        col1.append($(`<div class="chat-img-container"><img class="itemimage" src="${s3}dateSite/img/default_profile.png" alt="${user}"></div>`));
    }
    col1.append($('<div class="itemquantity">1</div>'));
    if (client.cliage == 0) {
        col2.append(`<span class="itemname">${user}</span>`);
    } else {
        col2.append(`<span class="itemname">${user},${client.cliage}</span>`);
    }
    col2.append(`<p class="itemmessage">${messageshort}</p>`);
    chat.append(col1).append(col2);
}

function addMessage(sender, message) {
    let clase = "bubble";
    if (sender == $('#sender').val()) {
        clase = "my-bubble";
    }
    let msg = `<div class="speech ${clase}">${message}</div>`;
    var ele = $('#chat-messages');
    ele.append(msg);
}

inList = function(lista, sender, messageshort) {
    let resp = false;
    let cantidad = $(`${lista}#client_${sender}`).length;
    if (cantidad > 0) {
        resp = true;
        let obj = $(`${lista}#client_${sender}`);
        if(sender == $("#sender").val()){
            //Coloquemos el badget
            cant = parseInt(obj.find(".itemquantity").text());
            cant++;
            if (cant > 9) {
                cant = "+9";
            }
            obj.find(".itemquantity").text(cant).show();
        }
        obj.find(".itemmessage").html(messageshort);
        var i = obj.index();
        if (i > 0) {
            let html = obj.html();
            let user = obj.attr("data-username");
            obj.remove();
            $(lista).parent().prepend($(`<li id='client_${sender}' data-username="${user}">${html}</li>"`));
        }
    }
    return resp;
}

function checkReadMessage(code) {
    $.ajax({
        url: '/ajax/checkReadMessage/',
        dataType: 'json',
        type: 'POST',
        data: {
            'code': code
        }
    });
}

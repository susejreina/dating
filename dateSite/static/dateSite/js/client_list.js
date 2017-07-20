function scrollActivity() {
    cargando = false;
    var $win = $(window);
    $win.scroll(function() {
        var winHeight = parseInt($win.height() + $win.scrollTop());
        var docHeight = parseInt($(document).height());
        var cerca = (docHeight * 95) / 100;
        if ((winHeight > cerca) && (cargando === false)) {
            loadMoreClients();
        }
    });
}

function loadMoreClients() {
    $('#loading').show();
    cargando = true;
    if ($("#show_more").val() == 0) {
        qty_clients = $("#ids").val().split(";").length;
        if (qty_clients < 18) {
            $('#loading').hide();
            var no_more_results = '<div class="noresults col-xs-12" id="nomoreresults">';
            no_more_results += '<p class="noresulttitle">NO MORE RESULTS</p>';
            no_more_results += '<p class="noresultmsg">Sorry we don\'t have more matches to show. Please, extend the range of the search filter.</p></div>';

            $("#members-content").append(no_more_results);
        } else {
            loadClientsFromClient();
            cargando = false;
            $('#loading').hide();
        }
    } else {
        getListMoreClients();
    }
}

function loadClientsFromClient() {
    var id_clients = $("#ids").val().split(";");
    var page = $("#page").val();
    var ini = page * 18;
    var end = ini + 17;
    page = page + 1;
    if (page >= parseInt($("#pages").val())) {
        page = 0;
    }
    $("#page").val(page);
    var clients_to_show = id_clients.slice(ini, end);
    for (c in clients_to_show) {
        var user = $("#member_" + clients_to_show[c]).attr("data-username");
        var html = `<li id="member_${clients_to_show[c]}" name="list_members" data-username="${user}">`;
        html += $("#member_" + clients_to_show[c]).html() + '</li>';
        $(".client-list").append(html);
    }
}

function getListMoreClients() {
    $.ajax({
        url: '/ajax/clients/',
        dataType: 'json',
        type: 'POST',
        data: {
            'min_age': $('#id_seaminage').val(),
            'max_age': $('#id_seamaxage').val(),
            'gencode': $('#id_gencode').val(),
            'country': $('#id_seacountry').val(),
            'ids': $('#ids').val()
        },
        complete: afterCallScroll,
        success: function(json_members) {
            members = JSON.parse(json_members["members"]);
            if (members.length == 0) {
                let content = '<div class="row noresults" id="nomoreresultsclient"><div class="col-xs-12"><p class="noresulttitle">NOT RESULTS FOUND</p>';
                content += '<p class="noresultmsg">Sorry we dont have any matches to show. Please open the value of the search filters.</p></div></div>';
                $("#members-content").html(content);
                $("#show_more").val(0);
                $("#pages").val(0);
            } else {
                let clase = "";
                if ($("#chat-box").is(":visible")) {
                    clase = "col-lg-6 col-md-6 col-sm-4 col-xs-6";
                } else {
                    clase = "col-lg-4 col-md-3 col-sm-4 col-xs-6";
                }
                for (var m in members) {
                    id = members[m].fields.pk;
                    username = members[m].fields.cliusername;
                    profile = members[m].fields.profile_picture;
                    verified = members[m].fields.cliverified;
                    gallery = members[m].fields.client_gallery;
                    feeling = members[m].fields.feecode;
                    birthdate = members[m].fields.clibirthdate;
                    age = members[m].fields.age;
                    city = members[m].fields.citcode;
                    showClientList(id, username, profile, verified, gallery, feeling, birthdate, age, city, clase);
                }
                $("#show_more").val(json_members["show_more"]);
                var pages = parseInt($("#pages").val()) + 1;
                $("#pages").val(pages);
            }
        },
        error: function() {
            console.log('Ajax error scrolling');
        },
    });
}

function afterCallScroll() {
    $('#loading').hide();
    cargando = false;
}

function showClientList(id, username, profile, verified, gallery, feeling, birthdate, age, city, clase) {
    html = `<li id="member_${id}" name="list-members" data-username="${username}">`;
    if (profile != null) {
        html += `<img src="${profile}" alt="${username}" title="${username}">`;
    } else {
        html += `<img src="${s3}dateSite/img/default_profile.png" alt="${username}" title="${username}">`;
    }
    if (verified) {
        html += `<div class="user-verified">`;
        html += `<img src="${s3}dateSite/img/user-verified.png" title="Verified member" data-toggle="tooltip">`;
        html += `</div>`;
    }
    html += `<div class="profile-info">`;
    html += `<div class="summary">`;
    html += `<div class="username">`;
    if (birthdate != null) {
        html += `${username}, ${age}`;
    }
    else{
        html += `${username}`;
    }
    html += `</div>`;
    html += `<div class="city">`;
    if (city != null) {
        html += city;
    }
    html += `</div>`;
    html += `<div class="btn-chat">CHAT NOW</div>`;
    html += `</div>`
    html += `<div class="feeling">`;
    if (feeling != null) {
        html += `<img src="${s3}dateSite/img/icons/${feeling}"`;
    }
    html += `</div>`;
    html += `</div>`;
    html += `</li>`;
    $(".client-list").append(html);

    var cad = $("#ids").val();
    cad = (cad == "" ? id : cad + ";" + id);
    $("#ids").val(cad);
}

$(document).ready(function() {
    if ($("#ids").val() != "0") {
        scrollActivity();
    }
    hyperLinks();
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

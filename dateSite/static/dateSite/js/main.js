$(document).ready(function() {
    if ($("#ids").val() != "0") {
        scrollActivity();
    }
    mainHyperLinks();
});

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
            let no_more_results = `<li class="no-results">`;
            no_more_results += `<p class="title">NOT RESULTS FOUND</p>`;
            no_more_results += `<p class="msg">Sorry we dont have any matches `;
            no_more_results += `to show. Please open the value of the search `;
            no_more_results += `filters.</p>`;
            no_more_results += `</li>`;

            $(".client-list").append(no_more_results);
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
                let content = `<li class="no-results">`;
                content += `<p class="title">NOT RESULTS FOUND</p>`;
                content += `<p class="msg">Sorry we dont have any matches to show. Please open the value of the search filters.</p>`;
                content += `</li>`;
                $(".client-list").html(content);
                $("#show_more").val(0);
                $("#pages").val(0);
            } else {
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
                    showClientList(id, username, profile, verified, gallery, feeling, birthdate, age, city);
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

function showClientList(id, username, profile, verified, gallery, feeling, birthdate, age, city) {
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

function mainHyperLinks() {
    //Link to profile view
    $(".content").on("click", ".client-list>li", function() {
        linkToProfile($(this));
    });
}

$(window).resize(function() {
    resize_album_preview();
    var w_chat = $(window).width();
    setTimeout(function() {
        collage();

    $('.thumbs-preview').css({
        'visibility': 'visible'
    });
    }, 900);
});
$(window).trigger('resize');

$(document).ready(function(e) {
    is_me = (user_pk == client_code ? true : false);
    albums_member(o_album_list);
    resize_album_preview();
    album_preview = localStorage.getItem('albumid');
    if (album_preview) {
        show_thumbs_gallery(album_preview);
        localStorage.removeItem('albumid');
    }
    $('#profile_percentage').attr('value', percentage);
    $("#close_big_picture").on("click", closeBigPicture);
    $(".profile_picture").on("click", ".picture", function() {
        see_picture($(this));
    });
    $(".thumbs-preview").on("click", ".thumb", function() {
        see_picture($(this));
    });
    setTimeout(function() {
        collage();
    }, 900);

    $(document).on('click', '.photo-gallery', function(e) { show_gallery(e) });
    $(document).on('click', '#add-album', function(e) { add_album(e) });
    $(document).on('click', '.show-pictures', function(e) { show_pictures(e) });
    $(document).on('click', '.fill-pic', function(e) { fill_pic(e) });
    $(document).on('click', '.qq-upload-button', upload_button)
    $('a#info_link').click(function(e) { info_link(e); });
    $('a#physical_link').click(function(e) { physical_link(e); });
    $('a#work_link').click(function(e) { work_link(e); });
    $('a#pass_link').click(function(e) { pass_link(e); });
    $("#btn-create-album").click(function() {create_album(); });
    $('#btn-go-top').click(function(e) { go_top(e); });
    document.onkeydown = checkKey;
    $("#left-arrow").click(function() { change_picture(37); });
    $("#right-arrow").click(function() { change_picture(39); });
    $('#id_phatype').change(function() { phatype_change(); });
    $('#privatealbumModal').on('shown.bs.modal', function(e) { purchase_private_album(e) });
    pictures_to_upload = false;
});

$(document).mouseup(function(e) {
    var container = $(".image-container, .arrow, .close_button");

    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0)
    {
        closeBigPicture();
    }
});

function show_gallery(e){
    var is_private = false;
    var album_id = $(e.target).data('albumid');
    if ($(e.target).attr('type') === '2') {
        is_private = true;
    }
    if (!is_private || private_collection.indexOf(album_id) !== -1) {
        show_thumbs_gallery(album_id);
    }
}

function add_album(e) {
    $('#uploadAlbumModal').modal('show');
}

function show_pictures(e) {
    $('#profilepicturesModal').modal('show');
    $("#btnYes").click(function() {
        if ($('.fill-pic [data-value="selected"]').attr('id') == null) {
            $('#msg').html("You haven't selected any picture yet");
            $('#body-select-pic').scrollTop(0);
        } else {
            $.ajax({
                type: 'POST',
                url: "/ajax/profile/picture",
                data: {
                    'picture_id': $('.fill-pic [data-value="selected"]').attr('id'),
                },
                success: function(data) {
                    $('#profilepicturesModal').modal('hide');
                    $('.pic-edit > img').attr('src', data.pic);
                    $('#menu-profile-pic').attr('src', data.pic);
                    $('#dropmenu-profile-pic').attr('src', data.pic);
                },
                error: function() {
                    console.log('Error get the pictures public albums');
                },
            });
        }
    });
    $('#btnCancel').click(function() {
        $('.fill-pic').css({
            'border': '2px solid #FFF',
            'box-shadow': 'none'
        });
    });
}

function fill_pic(e) {
    $('#msg').empty();
    $('.fill-pic').css({
        'border': '2px solid #FFF',
        'box-shadow': 'none'
    });
    $('.fill-pic > img').attr('data-value', 'none');
    $(e.target).closest("div").css({
        'border': '2px solid #07c',
        'box-shadow': '0 0 10px #07c'
    });
    $(e.target).attr('data-value', 'selected');
}

function upload_button() {
    $('#error-msg').empty();
    $('#error-msg').hide();
}

function info_link(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#basic_info').show();
}

function physical_link(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#physical_description').show();
}

function work_link(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#work_education').show();
}

function pass_link(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#change_pass').show();
}

function create_album() {
    var form_id = $("#upload-form > #id_form_id").val();
    if (!pictures_to_upload) {
        $('#error-msg').html("<label>You haven't selected any pictures</label>");
        $('#error-msg').show();
    } else {
        $.ajax({
            type: 'POST',
            url: '/ajax/create/album',
            data: {
                'album_name': $('#id_phaname').val(),
                'album_type': $('#id_phatype option:selected').val(),
                'form_id': form_id,
            },
            success: function(data) {
                if (data.error) {
                    $('.message-title').html('Info');
                    var msg = data.message;
                    if(data.type == "4"){
                        msg += '<br />Would you like to buy some? <a onclick="showModalByCredits()">Click here</a>';
                    }
                    $('#display-msg').html("<label class='modal-error'>" + msg + "</label>");
                    $('#messageModal').modal('show');
                } else {
                    json_data = JSON.parse(data);
                    $('#image_preview ').empty();
                    $('#uploadAlbumModal').modal('hide');
                    get_albums();
                    show_thumbs_gallery(json_data.id, json_data.album);
                    $("#credits_billing").text(json_data.credits);
                    $('.message-title').empty();
                    pictures_to_upload = false;
                    initUploadForm();
                }
            },
            error: function() {
                console.log('error create album');
            }
        });
    }
}

function go_top(e) {
    e.preventDefault();
    $('html,body').animate({
        scrollTop: 0
    }, 'fast');
}

function phatype_change() {
    if ($('#id_phatype').val() == "2") {
        $('#credits-warning').html('<label>Cost per album is 10 Credits.</label>');
    } else {
        $('#credits-warning').empty();
    }
}

function purchase_private_album(e) {
    e.preventDefault();
    var button = $(e.relatedTarget);
    var album_id = button.data('albumid');
    $('#btnYes').one('click', function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/ajax/add/private',
            data: {
                album_id: album_id,
            },
            cache: false,
            success: function(data) {
                if (data["error"]) {
                    $("#privatealbumModal").modal('hide');
                    $('#verifiedModal').modal('show');
                } else {
                    json_data = JSON.parse(data);
                    $('#privatealbumModal').modal('hide');
                    if (json_data.error != null) //has error
                    {
                        $('#errorModal').modal('show');
                        $('.modal-error-msg').html(json_data.error.message);
                    } else {
                        show_thumbs_gallery(album_id);
                        var img = $('.photo-gallery').find('img[data-albumid="'+album_id+'"]');
                        img.removeClass('blur');
                        manageBilling(json_data.credits, json_data.credits); //Just from one side
                        $('.album-preview > a > img').removeAttr('type');
                        $('.album-title > a').removeAttr('type');
                    }
                }
            },
            error: function() {
                console.log('Ajax error');
            },
        });
        return false;
    })
}

function show_thumbs_gallery(album_id, album_list) {
    var album_list = album_list || o_album_list;
    json_album_list = JSON.parse(album_list);
    var album_type = 1;
    var current_album;
    html = '';
    for (var album in json_album_list) {
        if (json_album_list[album].album.id == album_id) {
            current_album = album;
            html += '<div class="Collage">';
            pic_array = []
            for (var pic in json_album_list[album].pictures) {
                pic_array.push(json_album_list[album].pictures[pic].picpath);
            }
            for (var picture in json_album_list[album].pictures) {
                pic_id = json_album_list[album].pictures[picture].piccode;
                html += '<img id="' + pic_id + '" class="thumb" src="' + json_album_list[album].pictures[picture].picpath + '" data-pics="' + pic_array + '" data-index="' + picture + '" data-desc="' + json_album_list[album].pictures[picture].picdescription + '" data-id="' + pic_id + '"';
                if (json_album_list[album].album.type == '2') {
                    html += ' type="2"';
                    album_type = 2;
                }
                html += '/>';
            }
            html += '</div>'
            album_length = json_album_list[album].pictures.length;
        }
    }
    $('.thumbs-preview').css({
        'visibility': 'hidden'
    });
    $("#pictures-box").html(html);
    setTimeout(function() {
        collage();
        $('.thumbs-preview').css({
            'visibility': 'visible'
        });
    }, 500);
}

function collage() {
    $('.Collage').removeWhitespace().collagePlus({
        'targetHeight': 150,
        'effect': "effect-2",
        'fadeSpeed': 'fast',
        'allowPartialLastRow': false,
    });
}

function albums_member(album_list) {
    $("#albums-box").empty();
    if (album_list) {
        album_list = JSON.parse(album_list);
        if (album_list.length == 0) {
            $("#albums-box").append('<label class="message">No albums to show</label>');
            $('#albums-box').addClass('empty-albums-box');
        }
        for (var album in album_list) {
            if (album_list[album].pictures.length > 0) {
                html = '<div class="col-lg-2 col-md-3 col-xs-4 album-box">';
                html += '<div class="album-preview">';
                html += '<a class="photo-gallery" >';
                html += '<img data-albumid="' + album_list[album].album.id + '" src="' + album_list[album].pictures[0].picpath + '"';
                if (album_list[album].album.type == '2') {
                    if (!is_me && private_collection.indexOf(album_list[album].album.id.toString()) === -1) {
                        html += 'type="2" class="blur" data-toggle="modal" data-target="#privatealbumModal" data-albumid="' + album_list[album].album.id + '"';
                    }
                }
                html += '/></a>'
                if (is_me) {
                    html += '<a href="#" onClick="delete_album(' + album_list[album].album.id + ');" class="delete-element" title="Delete" data-toggle="tooltip">x</a>';
                }
                html += '</div>';
                html += '<label class="album-title"><a class="photo-gallery" data-albumid="' + album_list[album].album.id + '"';
                if (album_list[album].album.type == '2') {
                    if (!is_me && private_collection.indexOf(album_list[album].album.id.toString()) == -1) {
                        html += 'type="2" data-toggle="modal" data-target="#privatealbumModal"';
                    }
                }
                html += '>' + album_list[album].album.name + '</a></label>';
                html += '</div>';
                $("#albums-box").append(html);
            }
        }
    }
}

function resize_album_preview() {
    if ($(window).width() > 992) {
        var w = $(window).width() - $('.profile').width() - $('#chatContainer').width() - 50;
        $('#members-content').width(w);
        if ($('#members-content').width() < 140) {
            $('#members-content').hide();
            $('#btn-go-top').hide();
        } else {
            var clase;
            var remove = "col-lg-12 col-lg-4 col-lg-6";
            if ($('#members-content').width() < 250) {
                clase = "col-lg-12";
            } else if ($('#members-content').width() > 900) {
                clase = "col-lg-4";
            } else {
                clase = "col-lg-6";
            }
            $("div[name=list_members]").each(function() {
                $(this).removeClass(remove);
                $(this).addClass(clase);
            });
            $('#members-content').show();
            $('#btn-go-top').show();
        }
    }

    item_width = $('.album-preview').width();

    $('.album-preview').each(function() {
        $('.album-preview').height(item_width);
        $(this).find('img').css('width', '100%');
        $(this).find('img').css('min-height', '100%');
    });
    $('.thumbs-preview').css({
        'visibility': 'hidden'
    });
    setTimeout(function() {
        collage();
        $('.thumbs-preview').css({
            'visibility': 'visible'
        });
    }, 300);
}

function delete_album(album_id) {
    $('#modal-delete-title').html('Delete Album');
    $('#modal-delete-text').html('Are you sure want to delete this album?');
    $('#deleteelemModal').modal('show');
    $('#deleteelemModal').on('shown.bs.modal', function(e) {
        e.preventDefault();
        $('#btndeleteYes').unbind('click').click(function() {
            $.ajax({
                type: 'POST',
                url: '/ajax/delete/album',
                data: {
                    'album_id': album_id
                },
                success: function(data) {
                    $('#deleteelemModal').modal('hide');
                    get_albums();
                    album = JSON.parse(o_album_list)
                    show_thumbs_gallery(album[album.length - 1].album.id);
                }
            });
        });
        return false;
    });
};

function get_albums() {
    $.ajax({
        type: 'POST',
        url: "/ajax/get/albums",
        success: function(results) {
            o_album_list = results;
            albums_member(results);
            resize_album_preview();
        }
    });
}

function show_message(message) {
    // Remove the error element
    $('.message-title').html('Warning');
    $('#display-msg').html('<label>' + message + '</label>');
    $('#messageModal').modal('show');
}

function checkKey(e) {
    e = e || window.event;
    if (e.keyCode == '37' || e.keyCode == '39') {
        if (typeof index !== "undefined" && typeof pics !== "undefined") {
            change_picture(e.keyCode);
        }
    } else if (e.keyCode == '27') {
        if ($("#big_picture").is(":visible")) {
            closeBigPicture();
        }
    }
}

function change_picture(keyCode) {
    pics_array = pics.split(',');
    if (keyCode == '37') {
        if (index > 0) {
            index--;
        } else {
            index = pics_array.length - 1;
        }
    } else {
        if (index < pics_array.length - 1) {
            index++;
        } else {
            index = 0;
        }
    }
    var pic = $("img[src$='" + pics_array[index] + "']");
    if (pic.attr("type") !== "2") {
        $("#make_profile").show();
        $("#make_profile").attr('onclick', 'make_profile(' + id + ')');
    } else {
        $("#make_profile").hide();
    }
    get_description(pic.data('desc'));
    $("#make_profile").attr('onclick', 'make_profile(' + pic.data('id') + ')');
    $("#delete_picture").attr('onclick', 'delete_picture(' + pic.data('id') + ')');
    $("#picture_description").attr('onclick', 'picture_description("' + pics_array[index] + '")');
    img_size(pics_array[index]);
    $("#big_picture").attr("src", pics_array[index]);
    $("#big_picture").data("id", id);
}

function see_picture(obj) {
    var src = obj.attr("src");
    var img_type = obj.attr("type");
    index = obj.data('index');
    pics = obj.data('pics');
    description = obj.data('desc');
    id = obj.data("id");
    $("#picture-actions").show();
    $('.arrow').show();

    if (!id) {
        $("#picture-actions").hide();
    } else if (img_type === "3" || img_type === "2") {
        $("#make_profile").hide();
    } else {
        $("#make_profile").show();
        $("#make_profile").attr('onclick', 'make_profile(' + id + ')');
    }
    $("#delete_picture").attr('onclick', 'delete_picture(' + id + ')');
    $("#picture_description").attr('onclick', 'picture_description("' + src + '")');

    if (pics == null) {
        $('.arrow').hide();
    }
    get_description(description);
    img_size(src);
    $("#big_picture").attr("src", src);
    $("#big_picture").data("id", id);
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
        }
        else if (width > window.innerWidth) {
            var percentage = window.innerWidth * 90 / width / 100;
            height = height * percentage;
        }
        $('.image-container').height(height);
        $('.image-container').width(width);
    }
    img.src = src;
}

function get_description(description) {
    if (description != null && description != 'None' && description != "") {
        $("#picture_description").html('Edit description');
        $("#pic-desc").html('<label>' + description + '</label>')
        $("#pic-desc").show();
    } else {
        $("#picture_description").html('Add description');
        $("#pic-desc").hide();
    }
}

function closeBigPicture() {
    $("#pic-desc").hide();
    $("#inb_picture").hide();
}

function make_profile(id) {
    $('#profileModal').modal('show');
    $("#profileYes").click(function() {
        $.ajax({
            type: 'POST',
            url: "/ajax/profile/picture",
            data: {
                'picture_id': id,
            },
            success: function(picture) {
                $('#profileModal').modal('hide');
                closeBigPicture();
                $('#picture-preview').attr('src', picture.picpath);
                $('#menu-profile-pic').attr('src', picture.picpath);
                $('#dropmenu-profile-pic').attr('src', picture.picpath);
                $('#picture-preview').data('id', picture.pk);
                $('#picture-preview').data('desc', picture.picdescription);
                resize_album_preview();
                //traer de nuevo el album del cliente
                $.ajax({
                    type: 'POST',
                    url: '/ajax/get/album',
                    cache: false,
                    data: {
                        'albumid': picture.phacode,
                    },
                    success: function(results) {
                        var data = JSON.parse(results)[0];
                        show_thumbs_gallery(data.album.id, results);
                    }
                });
            },
            error: function() {
                console.log('Error to try make the profile picture');
            },
        });
    });
}

function picture_description(src) {
    var pic = $("img[src$='" + src + "']").filter(".thumb")[0];
    $('#picdescriptionModal').modal("show");
    var picture_description = $(pic).data('desc') == "None" ? "" : $(pic).data('desc');
    var path = $(pic).attr('src');
    $('#pic-desc-text').val(picture_description);
    $('#modal-picture').attr('src', path);
    $("#picdescriptionYes").one('click', function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/ajax/add/picture/description',
            data: {
                'picture_id': $(pic).data('id'),
                'description': $('#pic-desc-text').val(),
            },
            success: function(data) {
                $('#picdescriptionModal').modal('hide');
                description = $('#pic-desc-text').val();
                $(pic).data("desc", description);
                if (description) {
                    $("#pic-desc").html(description);
                    $("#pic-desc").show();
                } else {
                    $("#pic-desc").hide();
                }
            },
            error: function() {
                console.log('Error to add picture description');
            },
            cache: false,
        });
        $("#picdescriptionNo").click(function() {
            $('#pic-desc-text').val('');
        });
    });
}

function delete_picture(id) {
    $('#modal-delete-title').html('Delete Picture');
    $('#modal-delete-text').html('Are you sure want to delete this picture?');
    $('#deleteelemModal').modal('show');
    $('#deleteelemModal').on('shown.bs.modal', function(e) {
        e.preventDefault();
        $('#btndeleteYes').unbind('click').click(function() {
            $.ajax({
                type: 'POST',
                url: '/ajax/delete/picture',
                data: {
                    'picture_id': id
                },
                success: function(data) {
                    $('#deleteelemModal').modal('hide');
                    if (data.default) {
                        $("#picture-preview").attr('src', data.default);
                        $("#picture-preview").data('id', '');
                        $('#menu-profile-pic').attr('src', data.default);
                        $('#dropmenu-profile-pic').attr('src', data.default);
                    }
                    closeBigPicture();
                    get_albums();
                    show_thumbs_gallery(data.album_id, data.json_album);
                }
            });
        });
        return false;
    });
};

function initUploadForm() {
    initUploadFields($('#upload-form'), {
        validation: {
            allowedExtensions: ['jpg', 'png', 'jpeg'],
            sizeLimit: 3000000,
            minSizeLimit: 0,
            itemLimit: 10,
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
            onComplete: function(id, name, responseJSON, maybeXhr){
                pictures_to_upload = true;
            },
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            },
        },
        messages: {
            typeError: "{file} has an invalid extension. Only {extensions} images are allowed.",
            noFilesError: "No files to upload.",
            tooManyItemsError: "Images limit is {itemLimit} per album.",
            onLeave: "The files are being uploaded, if you leave now the upload will be canceled.",
        },
    });
}

function initPictureForm(){
    initUploadFields($('#update-profile'), {
        disableCancelForFormUploads: true,
        multiple: false,
        validation: {
            allowedExtensions: ['jpg', 'png', 'jpeg'],
            sizeLimit: 5000000,
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
            onComplete: function(id, name, responseJSON, maybeXhr){
                upload_profile_pic(responseJSON.filename, $('#update-profile').find('img').attr('src'));
            },
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            }
        },
    });
}

function upload_profile_pic(file, path){
    var old_src = $('#picture-preview').attr('src');
    $('#picture-preview').attr('src', path);
    $('.save-profile-pic, .cancel-profile-pic').show();
    $('.save-profile-pic, .cancel-profile-pic').css('z-index', '101');
    $('.update-profile-container').hide();
    $('.save-profile-pic').on('click', function() {
        save_uploaded_pic(file, old_src);
    });
    $('.cancel-profile-pic').on('click', function() {
        delete_uploaded_pic(file, old_src);
    });
}

function save_uploaded_pic(picture, path){
    $.ajax({
        type: 'POST',
        url: "/ajax/save/uploadedpicture",
        data: {
            'picture': picture,
        },
        success: function(data) {
            if(!data.success){
                msg = "The picture cannot be upload <br />" + data.error_message;
                show_message(msg);
                $('#picture-preview').attr('src', path);
            }
            else{
                $('.img-thumb').attr('src', data.picpath);
                $('#menu-profile-pic').attr('src', data.picpath);
                $('#picture-preview').data('id', data.piccode);
                $('#picture-preview').data('desc', data.picdescription);
                $.ajax({
                    type: 'POST',
                    url: '/ajax/get/album',
                    cache: false,
                    data: {
                        'albumid': data.phacode,
                    },
                    success: function(results) {
                        show_thumbs_gallery(data.phacode, results);
                    }
                });
            }
            $('.save-profile-pic, .cancel-profile-pic').hide();
            $('.save-profile-pic, .cancel-profile-pic').css('z-index', '99');
            $('.update-profile-container').show();
        },
    });
    initPictureForm();
}

function delete_uploaded_pic(picture, path){
    $.ajax({
        type: 'POST',
        url: "/ajax/delete/uploadedpicture",
        data: {
            'picture': picture,
        },
        success: function(data) {
            $('.save-profile-pic, .cancel-profile-pic').hide();
            $('.save-profile-pic, .cancel-profile-pic').css('z-index', '99');
            $('#picture-preview').attr('src', path);
            $('.update-profile-container').show();
        },
    });
    initPictureForm();
}

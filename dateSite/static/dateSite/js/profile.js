$(document).ready(function() {
    nameAlbum = $(".album-name").text();
    $(".modal").on("click", '.close', closeModal);
    $('.private').on('click', '.arrow', albumScroll);
    $(".private").on('click', '#add-album', function(){ $('#uploadAlbumModal').show(); });
    $(".inb_picture").on('click', '#left-arrow', function() { changePicture(37); });
    $(".inb_picture").on('click', '#right-arrow', function() { changePicture(39); });
    $(".inb_picture").on('click', '#close_big_picture', closeBigPicture);
    $(".inb_picture").on('click', '#action-options', optionsCollapse);
    $('.private-album').on('click', '.private-thumb', confirmPurchaseAlbum);
    $(".albums, .pic-container").on("click", ".thumb", seePicture);
    $("#album-box").on({mouseenter: setEditImage, mouseleave: removeEditImage}, '.album-name');
    $("#album-box").on("click", "#edit_album_name", editAlbumName);
    $("#album-box").on("click", "#accept_album_name", acceptEditAlbumName);
    $("#album-box").on("click", "#cancel_album_name", closeEditAlbumName);
    //$('#privatealbumModal').on('click', '#btnYes', confirmPurchaseAlbum);
    $('#deleteelemModal').on('click', '#btndeleteYes', confirmDelete);
    $("#profileModal").on('click', '#profileYes', makeMyProfilePic);
    $("#uploadAlbumModal").on('click', '.btn-primary, input[name="qqfile"]', function(){ $("#error-msg").empty(); });
    $("#uploadAlbumModal").on('click', '#btn-create-album', createAlbum);
    $('#picdescriptionModal').on('click', '#picdescriptionYes', saveDescription);
    $('#picdescriptionModal').on('click', "#picdescriptionNo", function() { $('#pic-desc-text').val('') });
    $('#profile_percentage').attr('value', percentage);
    initUploadForm();
    initPictureForm();
    document.onkeydown = checkKey;
    $("#picture-preview, .icon-pic, .photo").removeAttr('style');

    /* Edit profile page */
    $('#profile_percentage').attr('value', percentage);
    var d = new Date();
    $("#id_clibirthdate").datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: "1950:" + (d.getFullYear() - 18),
        dateFormat: "yy-mm-dd"
    });
    $(".picture-update").on('click', '.show-pictures', showPictures);
    $('#profilepicturesModal').on('click', "#btnYes", confirmMakeProfile);
    $('#profilepicturesModal').on('click', "#btnCancel", function() {$('.fill-pic').css({'border': '2px solid #FFF', 'box-shadow': 'none'}); });
    $("#body-select-pic").on('click', '.fill-pic', fillPic);
    /* End edit profile page */
});

window.onload = function () {
    $('#picture-preview').removeAttr('style');
}

$(window).resize(function() {
    var w_chat = $(window).width();
});

$(window).trigger('resize');

function setEditImage() {
    $(".album-button").html('<img src="' + s3 + 'dateSite/img/icons/edit-gray.png" id="edit_album_name" name="edit_album_name" class="edit-icon"/>').show().css('display', 'inline-flex');;
}

function removeEditImage() {
    $(".album-button").html("").hide();
}

function editAlbumName() {
    $(".album-description").hide();
    $(".album-input-description").show();
    setTimeout(function() {
        var editInput = $("#edit-album")
        var strLength = editInput.val().length * 2;
        editInput.focus();
        editInput[0].setSelectionRange(strLength, strLength);
    }, 1);
    var accept_button = '<img src="' + s3 + 'dateSite/img/accept-gray.png" id="accept_album_name" name="accept_album_name" class="icon"/>';
    var cancel_button = '<img src="' + s3 + 'dateSite/img/cancel-gray.png" id="cancel_album_name" name="cancel_album_name" class="icon"/>';
    $(".album-button").html(accept_button + cancel_button).show();
    $("#album-box").off('mouseenter mouseleave', '.album-name');
}

function closeEditAlbumName() {
    $(".album-button").html("").hide();
    $(".album-description").show();
    $(".album-input-description").hide();
    $("#album-box").on({
            mouseenter: setEditImage,
            mouseleave: removeEditImage
        },
        '.album-name');
}

function acceptEditAlbumName() {
    if (!$("#edit-album").val()) {
        show_message("Please enter an album name");
    } else {
        $.ajax({
            type: 'POST',
            url: '/ajax/album/name',
            data: {
                'album_id': $('.album-description').data('albumid'),
                'new_name': $("#edit-album").val(),
            },
            success: function(data) {
                if (data.error_message) {
                    show_message(data.error_message);
                } else {
                    $(".album-description").text($("#edit-album").val()).show();
                    $(".album-input-description").hide();
                    $("#pictures-box").on({
                            mouseenter: setEditImage,
                            mouseleave: removeEditImage
                        },
                        '.album-name');
                }
            }
        });
    }
}

$(document).mouseup(function(e) {
    var container = $(".image-container, .arrow, .close_button, #picdescriptionModal, #deleteelemModal");
    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0) {
        closeBigPicture();
    }
});

function createAlbum() {
    var form_id = $("#upload-form > #id_form_id").val();
    if (!pictures_to_upload || pictures_to_upload.length == 0) {
        $('#error-msg').html("<label>You haven't selected any pictures</label>");
        $('#error-msg').show();
    } else {
        $('#loading-image').show();
        $.ajax({
            type: 'POST',
            url: '/ajax/create/album',
            data: {
                'album_name': $('#id_phaname').val(),
                'album_type': $('#id_phatype option:selected').val(),
                'form_id': form_id,
            },
            success: function(data) {
                $('#loading-image').hide();
                if (data.error) {
                    $('.message-title').html('Info');
                    var msg = data.message;
                    $('#display-msg').html("<label class='modal-error'>" + msg + "</label>");
                    $('#messageModal').show();
                } else {
                    json_data = JSON.parse(data);
                    $('#error-msg').empty();
                    $('#error-msg').hide();
                    $('#id_phaname').empty();
                    $('#uploadAlbumModal').hide("slow");
                    $('.message-title').empty();
                    drawAlbums(json_data.albums);
                    initUploadForm();
                }
                pictures_to_upload = false;
                $('#image_preview ').empty();
            },
            error: function() {
                console.log('error create album');
            }
        });
    }
}

function drawAlbums(albums) {
    albums = JSON.parse(albums);
    var privates = '', publics = '';
    if (albums) {
        for (album in albums) {
            pics = []
            for (pic in albums[album].pictures) {
                pics.push(albums[album].pictures[pic]);
            }
            var d = '<a href="#" onClick="deleteAlbum(' + albums[album].code + ');" class="delete" title="Delete">x</a></div>'
            if(albums[album].type == "2"){
                privates += "<div class='private-album album-box'><img data-id='" + albums[album].code + "' src='" + pics[0].path + "' class='thumb' data-pics='" + JSON.stringify(pics) + "' data-index='0' data-desc='" + pics[0].description + "'>" + d;
            } else {
                publics += "<img data-id='" + albums[album].code + "' src='" + pics[0].path + "' class='thumb' data-pics='" + JSON.stringify(pics) + "' data-index='0' data-desc=''>" + d;
            }
        }
        $('.albums-row').html(privates);
        $('.public-album').html(publics);
    } else {
        html += '<label class="message">No albums to show</label>';
    }
}

function confirmPurchaseAlbum(){
    var album_id = $(this).data('id');
    $.ajax({
        type: 'POST',
        url: '/ajax/add/private',
        data: {
            'album_id': album_id,
        },
        success: function(data) {
            json_data = JSON.parse(data);
            if (!json_data.success) {
                $('#privatealbumModal').hide();
                $('.message-title').html('Oh no!');
                var msg = "Don't miss the chance to continue with this great adventure. <br /> Continue seeing the best and hottest pictures of all members. <a href='https://api.ccbill.com/wap-frontflex/flexforms/f34c27b0-2f5d-4a13-b382-2e04ba89f104?client=" + user + "' class='upgradePremiumModal' target='_blank'>Upgrate to premium.</a>";
                $('#display-msg').html("<label class='modal-error'>" + msg + "</label>");
                $('#messageModal').show();
            } else {
                $('#privatealbumModal').hide();
                $("#credits_billing").val(json_data.credits);
                var album = JSON.parse(json_data.album_added)[0];
                var pics = [];
                for (pic in album.pictures) {
                    pics.push(album.pictures[pic])
                }
                var img = $('.albums-row').find('img[data-id="' + album_id + '"]');
                img.addClass("thumb").removeClass("private-thumb");
                img.attr('data-pics', JSON.stringify(pics));
                img.attr('src', pics[0].path);
                img.attr('data-id', pics[0].code);
                img.attr('data-description', pics[0].description);
            }
        },
        error: function() {
            console.log('Ajax error');
        },
    });
}

function deleteAlbum(album_id) {
    $('#modal-delete-title').html('Delete Album');
    $('#modal-delete-text').html('Are you sure to delete this album?');
    $('#deleteelemModal').show();
    item_to_delete = album_id;
    all_album = true;
}

function deletePicture(id) {
    $('#modal-delete-title').html('Delete Picture');
    $('#modal-delete-text').html('Are you sure to delete this picture?');
    $('#deleteelemModal').show();
    item_to_delete = id;
    all_album = false;
}

function confirmDelete(){
    if(all_album){
        confirmDeleteAlbum();
    } else {
        confirmDeletePicture();
    }
}

function confirmDeleteAlbum() {
    $.ajax({
        type: 'POST',
        url: '/ajax/delete/album',
        data: {
            'album_id': item_to_delete,
        },
        success: function(data) {
            $('#deleteelemModal').hide();
            var img = $('.albums-row').find('img[data-id="' + item_to_delete + '"]');
            img.parent().remove();
        }
    });
}

function confirmDeletePicture() {
    $.ajax({
        type: 'POST',
        url: '/ajax/delete/picture',
        data: {
            'picture_id': item_to_delete
        },
        success: function(data) {
            $('#deleteelemModal').hide();
            if (data.default) {
                $("#picture-preview").attr('src', data.default);
                $("#picture-preview").data('id', '');
                $('#menu-profile-pic').attr('src', data.default);
                $('#dropmenu-profile-pic').attr('src', data.default);
            }
            closeBigPicture();
            drawAlbums(data.albums);
        }
    });
}

function checkKey(e) {
    e = e || window.event;
    if (e.keyCode == '37' || e.keyCode == '39') {
        if (typeof index !== "undefined" && typeof pics !== "undefined") {
            changePicture(e.keyCode);
        }
    } else if (e.keyCode == '27') {
        if ($("#big_picture").is(":visible")) {
            closeBigPicture();
        }
    }
}

function changePicture(keyCode) {
    pics_array = pics;
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
    $("#make_profile").attr('onclick', 'make_profile(' + pics_array[index].code + ')');
    get_description(pics_array[index].description);
    $("#make_profile").attr('onclick', 'make_profile(' + pics_array[index].code + ')');
    $("#delete_picture").attr('onclick', 'deletePicture(' + pics_array[index].code + ')');
    $("#picture_description").attr('onclick', 'pictureDescription("' + pics_array[index].description + '")');
    img_size(pics_array[index].path);
    $("#big_picture").attr("src", pics_array[index].path);
    $("#big_picture").data("id", id);
}

function seePicture(obj) {
    obj = $(this);
    var src = obj.attr("src");
    var img_type = obj.attr("type");
    index = obj.data('index');
    description = obj.data('description');
    id = obj.data('id');
    if(src.includes("default")){
        $("#picture-actions").hide();
    } else{
        pics = obj.data('pics');
        if(pics){
            id =  pics[index].code;
            src =  pics[index].path;
            $("#picture-actions").show();
            $('.arrow').show();
            $("#picture_description").attr('onclick', 'pictureDescription()');
            get_description(pics[index].description);
        } else { $('.arrow').hide(); }
    }
    img_size(src);
    if(img_type != "3"){
        $("#make_profile").show();
        $("#make_profile").attr('onclick', 'make_profile(' + id + ')');
    } else{ $("#make_profile").hide(); }
    $("#delete_picture").attr('onclick', 'deletePicture(' + id + ')');
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
    $('#profileModal').show();
    picture_id = id;
}

function makeMyProfilePic() {
    $.ajax({
        type: 'POST',
        url: "/ajax/profile/picture",
        data: {
            'picture_id': picture_id,
        },
        success: function(picture) {
            $('#profileModal').hide();
            closeBigPicture();
            $("#picture-preview").attr('src', picture.picpath);
            $('.img-thumb').attr('src', picture.picpath);
            $('#menu-profile-pic').attr('src', picture.picpath);
            $('.pic-edit > img').attr('src', picture.picpath);
            $('#picture-preview').data('id', picture.pk);
            $('#picture-preview').data('desc', picture.picdescription);
            drawAlbums(picture.albums);
        },
        error: function() {
            console.log('Error to try make the profile picture');
        },
    });
}

function pictureDescription() {
    var img = pics[index];
    $('#pic-desc-text').val(img.description);
    $('#modal-picture').attr('src', img.path);
    $('#picdescriptionModal').show();
    setTimeout(function(){
            $('#pic-desc-text').focus();
    }, 100);
    picture_id = img.code;
}

function saveDescription() {
    new_description = $('#pic-desc-text').val();
    $.ajax({
        type: 'POST',
        url: '/ajax/add/picture/description',
        data: {
            'picture_id': picture_id,
            'description': new_description,
        },
        success: function(data) {
            $('#picdescriptionModal').hide();
            description = $('#pic-desc-text').val();
            pics[index].description = new_description;
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
    });
}

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
            onAllComplete: function(id, name, responseJSON, maybeXhr) {
                pictures_to_upload = true;
            },
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            },
            onDelete: function(id) {
                var count = $('.qq-upload-delete').length;
                if (count <= 1) {
                    pictures_to_upload = false;
                }
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

function initPictureForm() {
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
            onComplete: function(id, name, responseJSON, maybeXhr) {
                upload_profile_pic(responseJSON.filename, $('#update-profile').find('img').attr('src'));
            },
            onError: function(id, name, reason, maybeXhrOrXdr) {
                show_message(reason);
            }
        },
    });
}

function upload_profile_pic(file, path) {
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

function save_uploaded_pic(picture, path) {
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
                $('.img-thumb').attr('src', data.picpath);
                $('#menu-profile-pic').attr('src', data.picpath);
                $('.pic-edit > img').attr('src', data.picpath);
                $('#picture-preview').data('id', data.piccode);
                $('#picture-preview').data('desc', data.picdescription);
                $('#profilepicturesModal').hide();
                drawAlbums(data.albums);
            }
            $('.save-profile-pic, .cancel-profile-pic').hide();
            $('.save-profile-pic, .cancel-profile-pic').css('z-index', '99');
            $('.update-profile-container').show();
        },
    });
    initPictureForm();
}

function delete_uploaded_pic(picture, path) {
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

function albumScroll(){
    if($(this).hasClass('left')){
        n = '-=200'
    } else{
        n = '+=200'
    }

    $('.albums-container').animate({
        scrollLeft: n
    }, 1000, 'easeOutQuad');
}

function show_message(message) {
    $('.message-title').html('Warning');
    $('#display-msg').html('<label>' + message + '</label>');
    $('#messageModal').show();
}

function showPictures() {
    $('#profilepicturesModal').show();
}

function confirmMakeProfile() {
    if (!picture_id) {
        $('#msg').html("You haven't selected any picture yet");
        $('#body-select-pic').scrollTop(0);
    } else {
        $.ajax({
            type: 'POST',
            url: "/ajax/profile/picture",
            data: {
                'picture_id': picture_id,
            },
            success: function(data) {
                $('#profilepicturesModal').hide();
                $('.img-thumb').attr('src', data.picpath);
                $('#menu-profile-pic').attr('src', data.picpath);
                $('.pic-edit > img').attr('src', data.picpath);
                $('#dropmenu-profile-pic').attr('src', data.picpath);
            },
            error: function() {
                console.log('Error get the pictures public albums');
            },
        });
    }
}

function fillPic() {
    $('#msg').empty();
    $('.fill-pic').css({
        'border': '2px solid #FFF',
        'box-shadow': 'none'
    });
    $('.fill-pic > img').attr('data-value', 'none');
    $(this).closest("div").css({
        'border': '2px solid #07c',
        'box-shadow': '0 0 10px #07c'
    });
    picture_id = $(this).find('img').attr('id');
}

function closeModal(){
    $(this).parents( ".modal" ).hide();
}

function optionsCollapse(){
    $("#list-btn").toggle();
}

//Show email confirmation message if user hasn't your email verified
$(document).ready(function() {
    s3 = $("#s3").val();
    s3_root = $("#s3_root").val();
    verify = $("#verified").val();
    let client = $("#is_client").val();
    if(client == 'True'){
        if(verify == 'False'){
            let title = "Verified your email";
            let content = "You are one step closer to start your adventure, ";
                content += "please confirm your email adress to create your ";
                content += "activate your account.<br /><br />";
                content += "DatingLatinos is always worry about antibot accounts."
            let contentTitle="Dear @User!";
            showModal(title,content,contentTitle,false,false);
        }
    }
    $(document).on("click", '#link_buy',function() {
        showModalByCredits();
    })
});

function showModal(title,contentMsg,contentTitle="",close=true,ok=true){
    $(".layer-header>.head-title").text(title);
    $(".layer-content>.cont-content").html(contentMsg);
    if(contentTitle!="")
        $(".layer-content>.cont-title").text(contentTitle);
    if(!close){
        $(".layer-header>.head-close").hide();
        $(".layer-footer>.foo-btn-close").hide();
    }
    else{
        $(".layer-header>.head-close, .layer-footer>.foo-btn-close").on("click",closeModal);
    }
    if(!ok){
        $(".layer-footer>.foo-btn-ok").hide();
    }
    $(".layer").show();
}

function closeModal(){
    $(".layer-header>.head-title").text("");
    $(".layer-content>.cont-content").html("");
    $(".layer-content>.cont-title").text("");
    $(".layer-header>.head-close").show();
    $(".layer-footer>.foo-btn-close").show();
    $(".layer-footer>.foo-btn-ok").show();
    $(".layer").hide();
}

function linkToProfile(obj) {
    var user = $(obj).attr("data-username");
    document.location.href = "/" + user;
}

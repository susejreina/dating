$(document).ready(function(){
    animation_main = 5000;
    initCarouselClient(".people>.itemstestimonials");
    carouselLoveStories();
    searchSmallDown();
});
function searchSmallDown(){
    if($(".search-label").is(':visible')){
        $(".search-label").click(function(){
            $( ".goodluckform" ).slideToggle( "slow" );
            $(".search-label").hide();
        });
        $(".search-arrow-down").on("click",function(){
            $( ".goodluckform" ).slideToggle("slow",function(){
                $(".search-label").show();
            });
        });
    }
}
function carouselLoveStories(){
    if($(".items-circles").is(":visible")){
        $(".stories>.itemslove:gt(0)").hide();
        $(".circle:eq(0)").addClass("circle-active");
        item_love_xm = 0;
        intervalLoveXm = setInterval(function(){
            caruselLoveXm();
        },animation_main);
    }
    else{
        storieSel=".stories>.itemslove";
        $(storieSel+":gt(2)").hide();
        if($(storieSel).length > 3){
            item_love_md = 2;
            setInterval(function(){
                $(storieSel+":lt(3)").fadeOut(3000,function(){
                    if(item_love_md<($(".stories-hidden>.love-elements").length-1)){
                        item_love_md=item_love_md+1;
                    }
                    else{
                        item_love_md=0;
                    }
                    var img_src=$(".stories-hidden>.love-elements:eq("+item_love_md+")").find("img").attr("src");
                    $(this).find("img").attr("src",img_src);
                    var p_html=$(".stories-hidden>.love-elements:eq("+item_love_md+")").find("p").html();
                    $(this).find("p").html(p_html);
                    $(this).fadeIn(3000);
                });
                },animation_main);
        }
    }
}
function caruselLoveXm(){
    $(".stories>.itemslove:eq("+item_love_xm+")").hide();
    $(".circle:eq("+item_love_xm+")").removeClass("circle-active");
    if(item_love_xm<($(".items-circles>.circle").length)-1){
        item_love_xm=item_love_xm+1;
    }
    else{
        item_love_xm=0;
    }
    $(".circle:eq("+item_love_xm+")").addClass("circle-active");
    $(".stories>.itemslove:eq("+item_love_xm+")").show();
}
function initCarouselClient(selector){
        current_item = Math.floor(parseFloat($(selector).length)/2);
        $(selector+":eq("+current_item+")>.itemname").show();
        $(selector+":eq("+current_item+")>img").animate({
            width: '98%',
            margin: '0px',
        },'fast',function(){
            interval=setInterval(function(){
                carouselClient(true, false, selector);
            },animation_main);
        });
        /* Eventos de las flechas y de los items */
        $(selector).click(function(){
            clearInterval(interval);
            carouselClient(false, $(this).index(), selector);
            interval=setInterval(function(){
                carouselClient(true, false, selector);
            },animation_main);
        });
}
function carouselClient(up, new_item, selector){
        var old_item =  current_item;
        var nro_testimonials = parseFloat($(selector).length)-1;
        if(new_item===false){
            if(up){
                if(current_item==nro_testimonials) current_item = 0;
                else current_item = current_item + 1;
            }
            else{
                if(current_item==0) current_item = nro_testimonials;
                else current_item = current_item - 1;
            }
        }
        else{
            current_item = new_item;
        }
        $(selector+":eq("+old_item+")>img").animate({
            width: '50%',
            marginLeft: '25%',
            marginRight: '25%',
            marginTop: '0px',
            marginBottom: '0px',
        },'fast',function(){
            $(selector+":eq("+old_item+")>.itemname").hide('fast',function(){
                $(selector+":eq("+current_item+")>.itemname").show('slow');
            });
            $(selector+":eq("+current_item+")>img").animate({
                width: '98%',
                marginLeft: '1%',
                marginRight: '1%',
                marginTop: '0px',
                marginBottom: '0px',
            },'slow');
        });
}

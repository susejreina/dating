/*
**	Anderson Ferminiano
**	contato@andersonferminiano.com -- feel free to contact me for bugs or new implementations.
**	jQuery ScrollPagination
**	28th/March/2011
**	http://andersonferminiano.com/jqueryscrollpagination/
**	You may use this script for free, but keep my credits.
**	Thank you.
*/

(function( $ ){

 $.fn.scrollPagination = function(options) {
		var opts = $.extend($.fn.scrollPagination.defaults, options);
		var target = opts.scrollTarget;
		if (target == null){
			target = obj;
	 	}
		opts.scrollTarget = target;

		return this.each(function() {
		  $.fn.scrollPagination.init($(this), opts);
		});

  };

  $.fn.stopScrollPagination = function(){
	  return this.each(function() {
	 	$(this).attr('scrollPagination', 'disabled');
	  });

  };

  $.fn.scrollPagination.loadContent = function(obj, opts){
	 var target = opts.scrollTarget;
	 var mayLoadContent = $(target).scrollTop() + opts.heightOffset >= $(document).height() - $(target).height();
     if (mayLoadContent){
         var json_data = read_data();
		 if (opts.beforeLoad != null){
			opts.beforeLoad();
		 }
		 $(obj).children().attr('rel', 'loaded');
		 $.ajax({
			  type: 'POST',
			  url: opts.contentPage,
              dataType: 'json',
			  data: {
                  'min_age': json_data[0].min_age,
                  'max_age': json_data[1].max_age,
                  'country': json_data[2].country,
                  'ids': json_data[3].list_id,
              },
			  success: function(json_members){
                members = JSON.parse(json_members["members"]);
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
                    showClientList(id,username,profile,verified,gallery,feeling,birthdate,age,city);
                }
                $("#show_more").val(json_members["show_more"]);
				var objectsRendered = $(obj).children('[rel!=loaded]');

				if (opts.afterLoad != null){
					opts.afterLoad(objectsRendered);
				}
			  },
			  error:function (){
				  console.log('Ajax error scrolling');
			  },
		 });
	 }

  };

  $.fn.scrollPagination.init = function(obj, opts){
	 var target = opts.scrollTarget;
	 $(obj).attr('scrollPagination', 'enabled');

	 $(target).scroll(function(event){
		if ($(obj).attr('scrollPagination') == 'enabled'){
	 		$.fn.scrollPagination.loadContent(obj, opts);
		}
		else {
			event.stopPropagation();
		}
	 });

	 $.fn.scrollPagination.loadContent(obj, opts);

 };

 $.fn.scrollPagination.defaults = {
      	 'contentPage' : null,
     	 'contentData' : {},
		 'beforeLoad': null,
		 'afterLoad': null	,
		 'scrollTarget': null,
		 'heightOffset': 0
 };
})( jQuery );

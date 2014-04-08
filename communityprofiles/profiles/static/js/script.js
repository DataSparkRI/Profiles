
$(function(){
	$('input, textarea').placeholder();
	// Drop-Down Buttons
	$("a.dd").live("click",function(){
		$(this).parent().find(".dd-content").toggle();
		return false;
	});

	$("div.col.fl.tour_2").live("mouseleave",function(){
		$(this).parent().find(".dd-content").hide();
		return false;
	});

	$("span#datadisplay_filter").live("mouseleave",function(){
		$(this).parent().find(".dd-content").hide();
		return false;
	});
	
	nav_update_parent();
	
	// Indicators Menu
	$("#DD-Indicator").live("click",function(){
		$("#Indicators-Menu").slideToggle(500,"easeInOutExpo");
		return false;
	});
	

	init_data_display_fb();
	init_data_display_sorting();

	$("td[rel=tooltip]").tooltip();
	$("th[rel=tooltip]").tooltip();
	$("div[rel=tooltip]").tooltip();
	
	$('.notes-icon').click(function(e){
		e.preventDefault();
		var selector = ".modal"+$(this).attr('href');
		var content_div = $(selector);
		var content = content_div.html();
	
		$.fancybox({
			'content': content_div.html(),
			'speedIn':160,
			'autoDimensions':false,
			'width':650,
			'speedOut':100,
			'padding':20,
			
		})
	});
	
	$('.about-indicator').click(function(e){
		e.preventDefault();
		$.fancybox({
			'content': $('.modal').html(),
			'speedIn':160,
			'speedOut':100,
			'autoDimensions':false,
			'width':650,
			'padding':20
			
		});

	});
	$('.about-indicator-inTable').click(function(e){
		e.preventDefault();
		$.fancybox({
			'content': $('.modal').html(),
			'speedIn':160,
			'speedOut':100,
			'autoDimensions':false,
			'width':650,
			'padding':20
			
		});

	});
	$('#Print-Button').click(function(e){
		e.preventDefault();
		var targ = $(this).attr("href");
		if(targ.indexOf("?") == -1){
			targ+="?&render=print";
		}else{
			targ+="&render=print";
		}
		window.location = targ;
	});

	if(typeof(cp_unsupported_browser)=='undefined'){
		$('.data-table').stickytable();
	}
	

	// Share Popup
	$('#Share-Button').live('click', function(){
		$(this).toggleClass("active").attr('class');
		$('#Share-Popup').toggle();
		return false;
	});
	
	$('#Export-Button').click(function(e){
		e.preventDefault();
		create_export_dialogue();
	});

	$('#Add').live('click', function(){
		$('#Add-Shelf-Popup').fadeOut(500);
		return false;
	});
	
	
	// Display Thumb Buttons (show)
	$("a.display-thumb").live("mouseenter",function(){
		$(this).addClass("active").next("div.display-thumb-btns").fadeIn(300);
		return false;
	});
	
	$("div.shelf-elements div.box").live("mouseleave",function(){
		$(this).children("a.display-thumb").removeClass("active").next("div.display-thumb-btns").fadeOut(300);
		return false;
	});
	
	
	$("div.search-category").live("click",function(){
		$(this).toggleClass("active").next("div.search-category-choices").slideToggle(500,"easeInOutExpo");
		return false;
	});
	
    $(".geo-nav ul li").tsort('a', {
        data:"sn"
    })


});



function findAddress(e){
	/*Requires that pp.js is loaded*/
	// Simple Client side validation
	e.preventDefault();
	$('#sba-input .geo-code-notice').remove();
	$('.popover').remove();
	
	var street = $('#sba-input #street').val();
	if(street===''){
		$("#search-by-address h2").text('Find An Address').fadeTo('fast', 0.3);
		$('#sba-input').prepend('<span class="error geo-code-notice"> <b>Street</b> Is Required</span>');
		return false;
	}

	var city = $('#sba-input #city').val();
	var zipcode = $('#sba-input #zipcode').val();
	$("#search-by-address h2").css('opacity', 1)
	$("#search-by-address h2").text('Searching...')
	// do the geo coding
	PP.XHR.geoCodeAddress(street,city, zipcode, function(data){
		$("#search-by-address h2").text('Find An Address').fadeTo('fast', 0.3);
		if(data.status == 'success'){
			// Use some Map methods to create a target path 
			var currURL = pm.homeLocation.split('/'); //gives us an array like so ["", "profiles", "state", "rhode-island", "overview", "income7", "?time=2006 - 2010"] We can then replace indexes where appropriate and then join the array to a string.
			// check for multiple
			
			if(data.results.length !==1){
			
				var m_alert = document.createElement('span');
				var html_out = '';
				m_alert.className="multi-geo";
				m_alert.className += " geo-code-notice";
				$(m_alert).text("Multiple Results Found...");
				var targURL = currURL;
				for(var i in data.results){
					targURL[2] = data.results[i].geography.level.slug;
					targURL[3] = data.results[i].geography.slug;
					html_out += '<a href="' + targURL.join('/') + '#LL=' + data.results[i].location.lat + "," +data.results[i].location.lng + "#PL="+encodeURIComponent(data.results[i].location.address) +'" class="geo-result">' + data.results[i].location.address + '</a>';
				}
				$('#sba-input').prepend(m_alert);
				// attach the popover
				$(m_alert).popover({
					'title': "We found " + data.results.length+ " matches",
					'placement':'bottom',
					'content':html_out,
					'trigger':'manual',
					'html':true
				});
				$(m_alert).popover('show');
			
				$('.popover').css({
					'left': parseFloat($(".popover").css('left').replace('px','')) + 150
						
				})
			}else{
				// Single Address
				// take them to that page
				var targURL = currURL;
				targURL[2] = data.results[0].geography.level.slug;
				targURL[3] = data.results[0].geography.slug;	
				window.location = targURL.join('/')+ "#LL="+data.results[0].location.lat+"," +data.results[0].location.lng + "#PL="+encodeURIComponent(data.results[0].location.address);
				//if we are still here
				pm.getPoint();
				
			}
		}else{
			$("#search-by-address h2").text('Find An Address').fadeTo('fast', 0.3);
			$('#sba-input').prepend('<span class="geocode-error geo-code-notice">Sorry, we were unable to find that address.</span>');
		}	
	});

}


//Data Display Fancybox
function init_data_display_fb(){
	// lets pass the windowWidth and height to the data display template

	$(".display-thumb").click(function(e){
		e.preventDefault();
		var ww = window.innerWidth;
		var wh = window.innerHeight;
		var href = $(this).attr("href") + "?ww=" + ww + "&wh=" + wh;
		$.fancybox({
			'href':href,
			'type':'iframe',
			'width':ww,
			'height':wh
		
		});
	
	});
}

// Data diplay time sorting
function init_data_display_sorting(){
	$("#datadisplay_filter li a").click(function(e){
		e.preventDefault();
		var elem = $(this);
		// hide everything currently visible
		$(".dd_active").addClass("dd_hidden").removeClass("dd_active");
		$("."+elem.attr("href")).removeClass("dd_hidden").addClass("dd_active");


	});

}

// Export dialogue
function create_export_dialogue(){

	// add click handler for export 
	$("#export-csv-btn a").live('click',function(){
		var export_url = "/profiles/export/";
		$("#export-form").attr('action', export_url);
		//$("#export-form").submit();
		
	});
	
	// pass it all to fancybox
	$.fancybox(content=$("#exporter").html());
}


function create_styled_btn(text,icon){
	var btn = document.createElement('span');
	btn.className = "buttons";
	btn.innerHTML = '<span class="buttons"><a><span class="sm-icon '+ icon+'"></span><span>'+text+'</span></a></span>';
	return btn;
}


// nav utils
//
function nav_update_parent(){
	$(".tab-links .subdomains .active").parent().parent().parent().children("a").addClass('active');
}

/*INDICATOR-VIEW*/

function init_indicator_view(slug, geo_slug){
	/*uses tastypie api*/
	var rqst_url = prof.base_url + "/api/v2/";
}


function capitalise(string){
    return string.charAt(0).toUpperCase() + string.slice(1);
}

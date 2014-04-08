/*
Original author Manoela Ilic
http://tympanus.net/codrops/2010/12/21/website-tour/
*/

$(function() {
	/*
	the json config obj.
	name: the class given to the element where you want the tooltip to appear
	bgcolor: the background color of the tooltip
	color: the color of the tooltip text
	text: the text inside the tooltip
	time: if automatic tour, then this is the time in ms for this step
	position: the position of the tip. Possible values are
		TL	top left
		TR  top right
		BL  bottom left
		BR  bottom right
		LT  left top
		LB  left bottom
		RT  right top
		RB  right bottom
		T   top
		R   right
		B   bottom
		L   left
	 */
	var config = [
	{
			"name" 		: ".tour_1",
			"bgcolor"	: "black",
			"color"		: "white",
			"title"		: "How to Find Your Community",
			"n_btn_txt"	: "",
			"text"		: "You can click on a town or city on the map to find your community.",
			"position"	: "L",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_2",
			//"bgcolor"	: "black",
			"color"		: "white",
			"n_btn_txt"     : "",
			"position"	: "T",
			"title"		: "How to Find Your Community",
			"text"		: "You can also use the drop-down menu to find your community.",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_3",
			"bgcolor"	: "black",
			"color"		: "white",
			"n_btn_txt"     : "",
			"title"     : "Explore the Data",
			"text"		: "Use the category tabs along the top to browse through the information available.",
			"position"	: "T",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_4",
			"bgcolor"	: "black",
			"color"		: "white",
			"n_btn_txt"     : "",
			"title"		: "The Data Table",
			"text"		: "This table will allow you to scroll through the indicators we have available in each category. Clicking on an indicator will map it on the geography you are currently viewing.",
			"position"	: "RT",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_5",
			"bgcolor"	: "black",
			"n_btn_txt"     : "",
			"color"		: "white",
			"title"		: "Search",
			"text"		: "Having trouble finding the data you're looking for?<br><br>Try using the search bar.",
			"position"	: "T",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_6",
			"bgcolor"	: "black",
			"n_btn_txt"     : "",
			"color"		: "white",
			"title"		: "Export, Share, and Print",
			"text"		: "Export will allow you to download the data you are viewing.<br><br>"+
			"Share your map with your friend on Facebook and Twitter.<br><br>Easily Print the map or save it to your computer.",
			"position"	: "BL",
			"time" 		: 5000
		},
		{
			"name" 		: ".tour_7",
			"bgcolor"	: "black",
			"color"		: "white",
			"n_btn_txt"     : "",
			"title"		: "Related Data Displays",
			"text"		: "These interactive maps and charts provide new ways to view and examine your data.<br><br>" +
			"Click on a chart to view it.",
			"position"	: "BL",
			"time" 		: 5000
		}
	],
	//define if steps should change automatically
	autoplay	= false,
	//timeout for the step
	showtime,
	//current step of the tour
	step		= 0,
	//total number of steps
	total_steps	= config.length;
		
	//show the tour controls
	//showControls();
	
	/*
	we can restart or stop the tour,
	and also navigate through the steps
	 */
	 if(window.location.hash == "#tour"){
	 	nextStep();
	 }

	//$('#user_guide').live('click',startTour);
	$('#user_guide').live('click', startTour);
	$('#canceltour').live('click', endTour);
//	$('#endtour').live('click',endTour);
//	$('#restarttour').live('click',restartTour);
	$('#nextstep').live('click',nextStep);
//	$('#prevstep').live('click',prevStep);

	function startTour(e){
		e.preventDefault();
		var domain = window.location.host;
		if(window.location.pathname != "/profiles/state/rhode-island/overview/"){
			window.location = "/profiles/state/rhode-island/overview/#tour";
			
		}
		nextStep();	
	}
	
	function nextStep(){
		if(!autoplay){
			if(step > 0)
				$('#prevstep').show();
			else
				$('#prevstep').hide();
			if(step == total_steps-1)
				$('#nextstep').hide();
			else
				$('#nextstep').show();	
		}	
		if(step >= total_steps){
			//if last step then end tour
			endTour();
			return false;
		}
		++step;
		showTooltip();
	}
/*	
	function prevStep(){
		if(!autoplay){
			if(step > 2)
				$('#prevstep').show();
			else
				$('#prevstep').hide();
			if(step == total_steps)
				$('#nextstep').show();
		}		
		if(step <= 1)
			return false;
		--step;
		showTooltip();
	}
*/	
	function endTour(){
		step = 0;
		//if(autoplay) clearTimeout(showtime);
		removeTooltip();
		//hideControls();
		//hideOverlay();
	}
/*	
	function restartTour(){
		step = 0;
		if(autoplay) clearTimeout(showtime);
		nextStep();
	}
*/	
	function showTooltip(){
		//remove current tooltip
		removeTooltip();
		
		var step_config		= config[step-1];
		var $elem			= $(step_config.name);
		
/*		if(autoplay)
			showtime	= setTimeout(nextStep,step_config.time);*/
		
	//	var bgcolor 		= step_config.bgcolor;
		var color	 		= step_config.color;

		html_str = '<p><strong>'+ step_config.title + '</strong><br>' +
						step_config.text +
						'</p><span class="close_tour" id="canceltour"></span>'+
						'<div><span class="tooltip_arrow"></span></div><div id="tour_btn_wrap">';
		if(step != config.length){
			html_str +=	'<span class="button_tour" id="nextstep">Next';
			next_step_config = config[step];
			html_str += next_step_config.n_btn_txt + '</span>';
		}
		else {
			html_str += '<span class="button_tour" id="nextstep">Start Exploring!</span>';
		}
/*		if(step != 1){
			html_str += '<span class="button_tour" id="prevstep">Previous</span>';
		}*/
		html_str +="</div>";
		
		var $tooltip		= $('<div>',{
			id			: 'tour_tooltip',
			html		: html_str
		}).css({
			'display'			: 'none',
//			'background-color'	: bgcolor,
//			'color'	: color
		});

		$tooltip.addClass("tooltip_tour");
		
		//position the tooltip correctly:
		
		//the css properties the tooltip should have
		var properties		= {};
		
		var tip_position 	= step_config.position;
		
		//append the tooltip but hide it
		$('body').prepend($tooltip);
		
		//get some info of the element
		var e_w	= $elem.outerWidth();
		var e_h	= $elem.outerHeight();
		var e_l	= $elem.offset().left;
		var e_t	= $elem.offset().top;
		
		
		switch(tip_position){
			case 'TL'	:
				properties = {
		'left'	: e_l,
		'top'	: e_t + e_h + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_TL');
				break;
			case 'TR'	:
				properties = {
		'left'	: e_l + e_w - $tooltip.width() + 'px',
		'top'	: e_t + e_h + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_TR');
				break;
			case 'BL'	:
				properties = {
		'left'	: e_l + 'px',
		'top'	: e_t - $tooltip.height() - 45 + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_BL');
				break;
			case 'BR'	:
				properties = {
		'left'	: e_l + e_w - $tooltip.width() + 'px',
		'top'	: e_t - $tooltip.height() + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_BR');
				break;
			case 'LT'	:
				properties = {
		'left'	: e_l + e_w + 'px',
		'top'	: e_t + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_LT');
				break;
			case 'LB'	:
				properties = {
		'left'	: e_l + e_w + 'px',
		'top'	: e_t + e_h - $tooltip.height() + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_LB');
				break;
			case 'RT'	:
				properties = {
		'left'	: e_l - $tooltip.width() - 25 + 'px',
		'top'	: e_t + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_RT');
				break;
			case 'RB'	:
				properties = {
		'left'	: e_l - $tooltip.width() + 'px',
		'top'	: e_t + e_h - $tooltip.height() + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_RB');
				break;
			case 'T'	:
				properties = {
		'left'	: e_l + e_w/2 - $tooltip.width()/2 + 'px',
		'top'	: e_t + e_h + 45 + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_T');
				break;
			case 'R'	:
				properties = {
		'left'	: e_l - $tooltip.width() - 25 + 'px',
		'top'	: e_t + e_h/2 - $tooltip.height()/2 + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_R');
				break;
			case 'B'	:
				properties = {
		'left'	: e_l + e_w/2 - $tooltip.width()/2 + 'px',
		'top'	: e_t - $tooltip.height() + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_B');
				break;
			case 'L'	:
				properties = {
		'left'	: e_l + e_w  + 25 + 'px',
		'top'	: e_t + e_h/2 - $tooltip.height()/2 + 'px'
				};
				$tooltip.find('span.tooltip_arrow').addClass('tooltip_arrow_L');
				break;
		}
		
		
		/*
		if the element is not in the viewport
		we scroll to it before displaying the tooltip
		 */
		var w_t	= $(window).scrollTop();
		var w_b = $(window).scrollTop() + $(window).height();
		//get the boundaries of the element + tooltip
		var b_t = parseFloat(properties.top,10);
		
		if(e_t < b_t)
			b_t = e_t;
		
		var b_b = parseFloat(properties.top,10) + $tooltip.height();
		if((e_t + e_h) > b_b)
			b_b = e_t + e_h;
			
		
		if((b_t < w_t || b_t > w_b) || (b_b < w_t || b_b > w_b)){
			$('html, body').stop()
			.animate({scrollTop: b_t}, 500, function(){
				//need to reset the timeout because of the animation delay
/*				if(autoplay){
		clearTimeout(showtime);
		showtime = setTimeout(nextStep,step_config.time);
				}*/
				//show the new tooltip
				$tooltip.css(properties).show();
			});
		}
		else
		//show the new tooltip
			$tooltip.css(properties).show();
	}
	
	function removeTooltip(){
		$('#tour_tooltip').remove();
	}
/*	
	function showControls(){
		/*
		we can restart or stop the tour,
		and also navigate through the steps
		 
		var $tourcontrols  = '<div id="tourcontrols" class="tourcontrols">';
		$tourcontrols += '<p>First time here?</p>';
		$tourcontrols += '<span class="button_tour" id="activatetour">Start the tour</span>';
			if(!autoplay){
				$tourcontrols += '<div class="nav_tour"><span class="button_tour" id="prevstep" style="display:none;">< Previous</span>';
				$tourcontrols += '<span class="button_tour" id="nextstep" style="display:none;">Next ></span></div>';
			}
			$tourcontrols += '<a id="restarttour" style="display:none;">Restart the tour</span>';
			$tourcontrols += '<a id="endtour" style="display:none;">End the tour</a>';
			$tourcontrols += '<span class="close_tour" id="canceltour"></span>';
		$tourcontrols += '</div>';
		
		$('body').prepend($tourcontrols);
		$('#tourcontrols').animate({'right':'30px'},500);
	}
	
	function hideControls(){
		$('#tourcontrols').remove();
	}
	
	function showOverlay(){
		var $overlay	= '<div id="tour_overlay" class="overlay_tour"></div>';
		$('body').prepend($overlay);
	}
	
	function hideOverlay(){
		$('#tour_overlay').remove();
	}
	*/
});

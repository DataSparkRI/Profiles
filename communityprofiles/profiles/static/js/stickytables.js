(function($){
	$.stickytable = function(el, options){
		// To avoid scope issues, use 'base' instead of 'this'
		// to reference this class from internal events and functions.
		var base = this;

		// Access to jQuery and DOM versions of element
		base.$el = $(el);
		base.el = el;

		// Add a reverse reference to the DOM object
		base.$el.data("stickytable", base);

		base.init = function(){
		    
		    base.options = $.extend({},$.stickytable.defaultOptions, options);
		    
		};

		// Run initializer
		base.init();
	};
    
	$.stickytable.defaultOptions = {

	};

    $.stickytable.elements = {};
	$.stickytable.get_styles = function(obj){
		var sheets = document.styleSheets;
		var iter;
		var rule;
		var styles = {};
		var rules = window.getComputedStyle(obj.get(0), null);
		var omit = ['-webkit-text-fill-color'];
		for(r in rules){
			iter= $.stickytable.isNum(r);
			if(iter !== false){
				if($.inArray(rules[r], omit) === -1){
					styles[rules[r]] = rules.getPropertyValue(rules[r]);
				}
			}
		}
		return styles;
	}

	$.stickytable.isNum = function(t){
		t = parseInt(t);
		if(isNaN(t)){
			return false;
		}else{
			return t;
		}

	}
    
	$.stickytable.css = function(a){
		var s = $.stickytable.get_styles(a);
		s['background'] = 'none';
		s['border'] = 'none';
		s['overflow'] = 'visible';
		s['overflowX'] = 'visible';
		s['overflowY'] = 'visible';
		s['padding'] = 0;
		s['color'] = '';
		return s;
	}

	$.stickytable.guid = function(){
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {var r = Math.random()*16|0,v=c=='x'?r:r&0x3|0x8;return v.toString(16);});
	}

	$.stickytable.check_loc = function(tbl){
		var sTop = tbl.p.scrollTop();
		var min = tbl.startY;
		var max = tbl.startY + tbl.t.outerHeight(true);
		if(sTop > min && sTop < max){
			if(tbl.c.css('display')=='none') tbl.c.css('display', 'inline-table');
		}else{
			tbl.c.css('display', 'none');
		}

	}

	$.stickytable.updated_p_styles = {
		margin:0,
		position:'relative',
		float:'none'
	}
    
    $.fn.stickytable = function(options){
	var self; // the table itself
	var tbl;
        return this.each(function(){
		(new $.stickytable(this, options));
		// store references
		self = $(this);
		var parent = self.parent();
		parent.scrollTop(0);
		var guid = $.stickytable.guid();
		
		//  wrap
		var wrap, p_styles;

		// sometimes they all live in the same element so... lets check for that before wrapping the parent over and over
		if(!parent.hasClass('stky-ct-el')){
			wrap = $(document.createElement('div'));
			wrap.addClass('stky-wrapper');
			// get styles and patch them!
			p_styles = $.stickytable.css(parent);
			if(!$.browser.msie) p_styles['width'] = parent.width();
			wrap.css(p_styles);
			
			parent.css($.stickytable.updated_p_styles);
		    parent.wrap(wrap);
			parent.addClass('stky-ct-el');
			wrap = parent.parent();
		}else{
			wrap = parent.parent();
		}
		// create our clone.
		var clone = self.clone();
		// get rid of useless nodes
		clone.children('tbody').remove();
		clone.css({
			display:'none',
			position:'absolute',
			'z-index':100,
			width:parent[0].scrollWidth,

		});
		clone.addClass('sticky-clone');
		wrap.prepend(clone);

		$.stickytable.elements[guid] = {
			t:self, 
			p:parent,
		       	c:clone, 
			startY:self.position().top
		};
		// attach a mouseevent handler to parent
		// at
		parent.scroll(function(e){
			tbl = $.stickytable.elements[guid];
			$.stickytable.check_loc(tbl);
		});

	    
        });
    };
    
})(jQuery);

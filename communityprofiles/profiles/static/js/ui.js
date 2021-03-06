/*Profiles UI*/

function init_ui(){


}

function sani_sel(selector){
    return selector.replace(/\s/g, "\\ ");
}


function tableize(selector, forceUpdate){
    /*
    if(angular.isUndefined(forceUpdate) || angular.isNull(forceUpdate)){
        forceUpdate = false;
    }
    
    var wrap = $(selector);
    wrap.addClass("tabilized");
    var th = $(selector + " thead");
    var tbody = $(selector + " tbody");
   
    var thPoss = th.position();
    var tb = $($(selector + " tbody tr").get(0));
    var ths = tb.children('td:not(.ng-hide)');
    var w = wrap.width();
    var td_width = parseFloat(w)/parseFloat(ths.length);
    var td;
    
    th.css({
        position:'fixed',
        top:wrap.offset().top,
        left:wrap.offset().left,
        width:w,
    });

    th.children("tr").css({
        display:'inline-table',
        width:"100%",
    });

    tbody.css({
        width: w,
        display:'inherit',
    });
    th.find("th").css({
        width:td_width 
    })
    tbody.find("td").css({
        width:td_width   
    });*/
}

function initScrollSpy(){
    var b = $(window);
    var wH = b.height()/2;
    var f = $("#f-foot");
    f.click(function(){
        b.scrollTop(0);   
    })
    b.scroll(function(e){
        if(b.scrollTop()>150){
            f.show();
        }else{
            f.hide();
        }   
    });
}

$(function ()  
{ $(".domain-title").popover({});  
});


(function(e,t){"use strict";function i(i,s){var n=this;n.$el=e(i),n.el=i,n.id=a++,n.$el.bind("destroyed",e.proxy(n.teardown,n)),n.$clonedHeader=null,n.$originalHeader=null,n.isSticky=!1,n.hasBeenSticky=!1,n.leftOffset=null,n.topOffset=null,n.init=function(){n.options=e.extend({},o,s),n.$el.each(function(){var t=e(this);t.css("padding",0),n.$scrollableArea=e(n.options.scrollableArea),n.$originalHeader=e("thead:first",this),n.$clonedHeader=n.$originalHeader.clone(),t.trigger("clonedHeader."+l,[n.$clonedHeader]),n.$clonedHeader.addClass("tableFloatingHeader"),n.$clonedHeader.css("display","none"),n.$originalHeader.addClass("tableFloatingHeaderOriginal"),n.$originalHeader.after(n.$clonedHeader),n.$printStyle=e('<style type="text/css" media="print">.tableFloatingHeader{display:none !important;}.tableFloatingHeaderOriginal{position:static !important;}</style>'),e("head").append(n.$printStyle)}),n.updateWidth(),n.toggleHeaders(),n.bind()},n.destroy=function(){n.$el.unbind("destroyed",n.teardown),n.teardown()},n.teardown=function(){n.isSticky&&n.$originalHeader.css("position","static"),e.removeData(n.el,"plugin_"+l),n.unbind(),n.$clonedHeader.remove(),n.$originalHeader.removeClass("tableFloatingHeaderOriginal"),n.$originalHeader.css("visibility","visible"),n.$printStyle.remove(),n.el=null,n.$el=null},n.bind=function(){n.$scrollableArea.on("scroll."+l,n.toggleHeaders),n.$scrollableArea[0]!==t&&(e(t).on("scroll."+l+n.id,n.setPositionValues),e(t).on("resize."+l+n.id,n.toggleHeaders)),n.$scrollableArea.on("resize."+l,n.toggleHeaders),n.$scrollableArea.on("resize."+l,n.updateWidth)},n.unbind=function(){n.$scrollableArea.off("."+l,n.toggleHeaders),n.$scrollableArea[0]!==t&&(e(t).off("."+l+n.id,n.setPositionValues),e(t).off("."+l+n.id,n.toggleHeaders)),n.$scrollableArea.off("."+l,n.updateWidth),n.$el.off("."+l),n.$el.find("*").off("."+l)},n.toggleHeaders=function(){n.$el&&n.$el.each(function(){var i,l=e(this),a=n.$scrollableArea[0]===t?isNaN(n.options.fixedOffset)?n.options.fixedOffset.height():n.options.fixedOffset:n.$scrollableArea.offset().top+(isNaN(n.options.fixedOffset)?0:n.options.fixedOffset),o=l.offset(),s=n.$scrollableArea.scrollTop()+a,r=n.$scrollableArea.scrollLeft(),d=n.$scrollableArea[0]===t?s>o.top:a>o.top,c=(n.$scrollableArea[0]===t?s:0)<o.top+l.height()-n.$clonedHeader.height()-(n.$scrollableArea[0]===t?0:a);d&&c?(i=o.left-r+n.options.leftOffset,n.setPositionValues(),n.$originalHeader.css({position:"fixed","margin-top":0,left:i,"z-index":1}),n.isSticky=!0,n.leftOffset=i,n.topOffset=a,n.$clonedHeader.css("display",""),n.updateWidth()):n.isSticky&&(n.$originalHeader.css("position","static"),n.$clonedHeader.css("display","none"),n.isSticky=!1,n.resetWidth(e("td,th",n.$clonedHeader),e("td,th",n.$originalHeader)))})},n.setPositionValues=function(){var i=e(t).scrollTop(),l=e(t).scrollLeft();!n.isSticky||0>i||i+e(t).height()>e(document).height()||0>l||l+e(t).width()>e(document).width()||n.$originalHeader.css({top:n.topOffset-(n.$scrollableArea[0]===t?0:i),left:n.leftOffset-(n.$scrollableArea[0]===t?0:l)})},n.updateWidth=function(){if(n.isSticky){var t=e("th,td",n.$originalHeader),i=e("th,td",n.$clonedHeader);n.cellWidths=[],n.getWidth(i),n.setWidth(i,t),n.$originalHeader.css("width",n.$clonedHeader.width())}},n.getWidth=function(t){t.each(function(t){var i,l=e(this);i="border-box"===l.css("box-sizing")?l.outerWidth():l.width(),n.cellWidths[t]=i})},n.setWidth=function(e,t){e.each(function(e){var i=n.cellWidths[e];t.eq(e).css({"min-width":i,"max-width":i})})},n.resetWidth=function(t,i){t.each(function(t){var l=e(this);i.eq(t).css({"min-width":l.css("min-width"),"max-width":l.css("max-width")})})},n.updateOptions=function(t){n.options=e.extend({},o,t),n.updateWidth(),n.toggleHeaders()},n.init()}var l="stickyTableHeaders",a=0,o={fixedOffset:0,leftOffset:0,scrollableArea:t};e.fn[l]=function(t){return this.each(function(){var a=e.data(this,"plugin_"+l);a?"string"==typeof t?a[t].apply(a):a.updateOptions(t):"destroy"!==t&&e.data(this,"plugin_"+l,new i(this,t))})}})(jQuery,window);

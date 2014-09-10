/* Map tools for embedding leaflet maps in profiles and other places.
   profiles_maps consumes profiles geo_json apis and its data api.
   Requires pp.js
*/

var profilesMapActiveLayers = {};
var _profilesMapMethods={};
var _profilesMapRolloverCallbacks = [];
var _profilesMapRolloutCallbacks = [];
var _profilesMapClickCallbacks = [];

function ProfilesMap(){
	this.defaultView;
	this.defaultZoom = 10;
	this.mapDivId = 'map';
	this.maxZoom = 18;
	this.map;
	this.nbreaks;
	this.layers; // all layers are containd in this main L.featureGroup
	this.colorList = ["#E4F7FF", "#AADFF7", "#72B5F2", "#3383e5", "#2767dd", "#345999"];
	this.homeLocation;
	this.managedLayers = []; //push an array into this list [<Layer>,<zoom_theshold>] what i really want is a tuple :(
	this.defaultStyle = {color:"#444", opacity:.4, fillColor:"#72B5F2", weight:1, fillOpacity:0.6};
	this.polys; // keeps track of the polys add to our map
        this.controls;

}

ProfilesMap.prototype.init = function(){
	var self = this;
	self.polys = {};

	var esri_imagery = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri',
		maxZoom: 16
	});

	var esri_gray = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri',
		maxZoom: 16
	});

	this.map = L.map(this.mapDivId, { zoomControl: true, layers: [esri_imagery, esri_gray]}).setView(this.defaultView, this.defaultZoom);

	this.controls = L.control.layers({"Imagery": esri_imagery, "Gray": esri_gray}, {}, {position: 'topleft'}).addTo(this.map);

	this.map.on('zoomend',function(){
		self.updateLayers(self.map.getZoom());
	});
	this.layers = L.featureGroup([]);// instantiate our mininum layerGroup
	this.layers.addTo(this.map);
	// create homeButton
	this.createHomeButton();
	this.getPoint();
}

ProfilesMap.prototype.createHomeButton = function(){
	var self = this;
	var homeButton = L.control();
	homeButton.onAdd = function(map){
		this._div = L.DomUtil.create('div', 'map-home-btn'); // create a div with a class "homebutton"
		this._div.innerHTML = '<a href="#"></a>';
		return this._div;
	}
	
	homeButton.setPosition('topleft');
	homeButton.addTo(this.map);

	$(".map-home-btn a").click(function(e){
		// navigate whatever homeLocation is	
		e.preventDefault();
		window.location = self.homeLocation;
	});

}

ProfilesMap.prototype.createGeoJsonLayer = function(feat, style, funcList){
	/*Creates a L.geoJsonLayer
	 * <feat> a geojson feature
	 * <funcList> object like this {mouseover:func, mouseout:func, click:func}
	 * <style> a style object
	*/
	var self = this;
	if(typeof(style)==='undefined' || style===null){ 
		style = self.defaultStyle;
	}
	if(typeof(funcList) ==='undefined'){
		funcList = {}
	}
	var layer = L.geoJson(feat, {
			style:style,
	    		onEachFeature:self.createFeatureMouseHandlers(funcList)
	});
	
	return layer;

}

ProfilesMap.prototype.createGeoPolyLayer = function(feat, style, funcList){
	return this.createGeoJsonLayer(feat, style, funcList);
}

ProfilesMap.prototype.createGeoLineStringLayer = function(feat, style, funcList){
	return this.createGeoJsonLayer(feat, style, funclist);
}

ProfilesMap.prototype.addPointOverlay = function(title, data){
	var self = this;

	var overlay = L.geoJson(data, {
            onEachFeature: function(feature, layer) {
                layer.setIcon(L.icon({
                          iconUrl: feature.properties.image,
                          iconSize: [30, 30]
                      }))
                     .bindPopup(feature.properties.label);
            }
	});
	
        this.controls.addOverlay(overlay, title);
}

ProfilesMap.prototype.createGeoLabelLayer = function(feat, style){
	/*Creates a L.geoJsonLayer with divIcon for Marker
	 * TODO: should this accept funcList?*/
	var self = this;

	if(typeof(style)==='undefined' || style===null){ 
		style = self.defaultStyle;
	}
	var icon = L.divIcon({html:'<span style="color:'+style.color+';">'+feat.label+'</span>', className:'divicon'});
	var layer = L.geoJson(feat.geom, {
		pointToLayer: function (feature, latlng){
			 marker = L.marker(latlng, {icon:icon});
			 return marker;
		}
	});

	return layer;
}


ProfilesMap.prototype.getPoint = function (){
	/*Checks for location has in url bar*/
	var geocode_rx = new RegExp(/#LL=[0-9\.,-]+/);
	var place_rx =  new RegExp(/PL=[a-zA-Z0-9%%\.\s]+/);
	var gc_match; // geocode match
	var pl_match; // place match in name
	var coords;
	var place_match;
	if(geocode_rx.test(window.location.hash)){
		// this has a hash, lets try to match our keywords
		gc_match = geocode_rx.exec(window.location.hash)[0].replace("#LL=",'');
		coords = gc_match.split(',');
		var marker = this.createMarker(coords[0],coords[1]).addTo(this.map);

		if(place_rx.test(window.location.hash)){
			pl_match = place_rx.exec(window.location.hash)[0].replace("PL=","");
			marker.bindPopup(decodeURIComponent(pl_match)).openPopup();
			
		}
	}

}

ProfilesMap.prototype.createMarker = function(lat,lng){
	var self = this;
	var m = L.marker([lat,lng]);
	return m;
}

ProfilesMap.prototype.DataFeatureGroup = function(data, style, funcList){
	/*
	 * Creates and returns a L.featureGroup from a Profiles GeoJson data set.
	 *
	 * */
	var self = this;
	var layers = [];
	data = data.hasOwnProperty('objects') ? data.objects : data;
	for(var i in data){
        //try{
		    layers.push(self.createGeoPolyLayer(data[i], style, funcList));
        //}catch(e){
          //  console.log(e)
        //}
	}
	return L.featureGroup(layers);
}

ProfilesMap.prototype.DataPolyFeatureGroup = function(data, style, funcList){
	return this.DataFeatureGroup(data, style, funcList);
}

ProfilesMap.prototype.DataLStringFeatureGroup = function(data, style, funcList){
	return this.DataFeatureGroup(data, style, funcList);
}

ProfilesMap.prototype.DataLabelFeatureGroup = function(data, style){
	/*
	 * Creates and returns a L.featureGroup from a Profiles GeoJson data set.
	 *
	 * */
	var self = this;
	var layers = [];
	data = data.hasOwnProperty('objects') ? data.objects : data;
	for(var i in data){
		layers.push(self.createGeoLabelLayer(data[i], style));
	}

	return L.featureGroup(layers);
}

ProfilesMap.prototype.DataChoroplethFeatureGroup = function(data, valueKey, funcList, bin, formatter, legText){
	/**
	 * .. and then I read about how to properly document JS code.
	 * @method DataChoroplethFeatureGroup
	 * @param {Object} data A Profiles GeoJson object
	 * @param {String} ?
	 * @param {Object} A Object of valid Leaflet MouseHandlers
     * @param {Object} A valid classifier type See Below
	 * @return {L.featureGroup} Return colorized feature group
     *
     * bin:
     * Profiles map supports 5 types of data classifier bins
     * Equally Spaced: eq
     * Custom Breaks: cb 
     * Equal Interval: ei
     * All Categories: all
	 * */

	if(typeof(valueKey) ==='undefined' || valueKey==null) valueKey = 'number';
    if(typeof(bin) ==='undefined' || bin==null) bin = {bin_type:'jenks', bin_options:5}; // default classifier Equally spaced with 5 bins
	if(typeof(formatter) ==='undefined' || formatter==null) formatter = {'type':'count'}; // the number formatter. Defaults to count
    // we need to account for formatting percents here. This is a bit fragile and i dont like it.
    if(valueKey=='percent'){
        formatter = {'type':'percent'};
    }

	var self = this;
	var layers = [];
	var style = {
		fillColor: 'blue',
		weight: 1,
		opacity: 0.8,
		color:'#fff',
		fillOpacity: 0.8
	}
	var values = [];
	var fvalues = {};
	var obj;
	var cval; // current Value
	var v;
    var value_bin; // the bin generated from the data based on bin option
    var data_values = []; // this is just a collection of value objects
    // we need to iterate over all the data objects, extracting the values so we can then bin them
    for(var i in data.objects){
        obj = data.objects[i];
        if(obj.values!==null){
            obj.values['label'] = obj.properties.label;
            data_values.push(obj.values);
            if(self.valid_moe(obj.values)){
                if (parseFloat(obj.values[valueKey]) == 0 )
                    v = parseFloat(obj.values[valueKey])
                else
                    v = parseFloat(obj.values[valueKey]) || -999999; // value or -99999 . -99999 here is a null value
                values.push(v);
                //fvalues[v] = obj.values["f_"+valueKey];

            }else{
                if(!fvalues.hasOwnProperty('-999999')){
                        values.push(-999999);
                        fvalues['-999999'] = 'MoE larger than estimated value'
                }
            }
        }else{
        }
    }

	if(values.length > 0){
        /*bin the values */
        var unique_vals = new geostats(values);
        unique_vals = unique_vals.getUniqueValues();
        if(unique_vals.length > 2){
            switch(bin.bin_type){
                case 'eq':
                    value_bin = self.makeBins(self.binEqSpaced(values, bin.bin_options));
                break;
                case 'cb':
                    value_bin = self.makeBins(self.binCustomBreak(bin.bin_options));
                break;
                case 'ei':
                    value_bin = self.makeBins(self.binEqInt(values, bin.bin_options));
                break;
                case 'all':
                    value_bin = self.makeBins(self.binAll(values), false);
                break;

                case 'jenks':
                    value_bin = self.makeBins(self.binJenks(values, bin.bin_options));
                break;

                default:
                    value_bin = self.makeBins(self.binJenks(values, bin.bin_options));

            }
        }else{
            // if there are fewer than 3 items in the data just return an 'all' bin
            value_bin = self.makeBins(self.binAll(values), false);
            
        }

        // Now interate the data and create geopolys
        for(var i in data.objects){
            obj = data.objects[i];
             if(obj.values != null){
                if (obj.values[valueKey] == 0)
                   cval = 0
                else
                   cval = obj.values[valueKey] || -999999; // the actual value

                var valid_moe = true;
                // this is a regular value
                if(!self.valid_moe(obj.values)){
                        valid_moe = false;
                }else{
                        valid_moe = true;
                }
                if(valid_moe){
                    style.fillColor = self.getColor(cval, value_bin);
                    try{
                        layers.push(self.createGeoPolyLayer(data.objects[i], style, funcList));
                    }catch(e){
                        //..
                    }
                }else{
                    var b_style = {}; 
                    $.extend(b_style, style);
                    b_style.fillColor = "#999"; // this means there is no value for this poly
                    try{
                        layers.push(self.createGeoPolyLayer(data.objects[i], b_style, funcList));
                    }catch(e){
                        //...
                    }

                }
             }else{
             }
        }
		return [L.featureGroup(layers), self.createChroplethLegend(value_bin, 'bottomleft', formatter, legText)];
	}else{
		return false;
	}


}

ProfilesMap.prototype.getFormatter = function(formatter){
    var self = this;
    var format_func;
    switch(formatter.type){
        case 'count':
            format_func = function(value){
                return self.formatCount(value);
            }
        break;
        case 'dollars':
            format_func = function(value){
                return self.formatDollar(value);
            }
        break;
        case 'year':
           format_func = function(value){
                return value;
            }
        break;
         case 'percent':
            format_func = function(value){
                return self.formatPercent(value);
            }
        break;
        case 'custom':
            format_func = function(value){
                return self.formatCustom(value, formatter.rules);
            }
        break;

        default:
            format_func = function(value){
                return self.formatCount(value);
            }
             
    }
    return format_func;
}


ProfilesMap.prototype.createChroplethLegend = function(value_bins, position, formatter, headingText){
    /*
     * Create a legend for this value_bin
     * */
	var self = this;
	var legend = L.control({position: position});
	var ref = {};
    var txt;
    var format_func = self.getFormatter(formatter);

	legend.onAdd = function(map){
		var div = L.DomUtil.create('div', 'info legend');
        if(headingText !== undefined){
            div.innerHTML += headingText;
        }
        
        for(var i in value_bins){
            var bin = value_bins[i];
            div.innerHTML +='<i><svg height="18" width="18"><rect height="18" width="18" fill="'+ bin.color+ '"></svg></i>';
            if(bin.values.length == 2){ // bins can either have 2 elements or 3 elments with the last elem always being the color
                div.innerHTML += format_func(bin.values[0]) + " &ndash; " + format_func(bin.values[1]);
            }else if(bin.values.length == 1){
                div.innerHTML += format_func(bin.values[0]);
            }
            div.innerHTML += "</br>";
        }
		return div;

	};// end onAdd*/
	return legend;
}


ProfilesMap.prototype.highlightGeoLayer = function(geoName, colorize){
	/* Highlight and center on a geography */
	var self = this;
	var layer;
	if(self.polys.hasOwnProperty(geoName)){
		layer = self.polys[geoName];
		if(colorize==true){
			layer.setStyle({fillColor:"#ffe821"});
		}else{
			layer.setStyle({weight:3, color:'#000', dashArray:'10'});
		}
        try{
            layer.bringToFront();
        }catch(e){
            //...
        }
		self.map.fitBounds(layer.getBounds());
	}else{
		return false;
	}
}

ProfilesMap.prototype.getCodeInfo = function(value){
	switch(value){
        case -1:
            return ['#e3e3e3', "-1"];
        break;
		case -999999:
			return ['#999', 'MoE larger than estimated value'];
		break;
	}
}


/*MOUSE EVENTS*/

ProfilesMap.prototype.createFeatureMouseHandlers = function(funcLists){
	if(typeof(funcList)==='undefined'){
		funcList = {};
	}
	return function(feature, layer){
		layer.on(funcLists);
	}
}


ProfilesMap.prototype.highlightLayer = function(e){
	var layer = e.target;
	// change the style of the layers on rollover
	if(layer.hasOwnProperty('_layers')){
		for(l in layer['_layers']){
			profilesMapActiveLayers[layer._leaflet_id] = layer['_layers'][l].options;
			layer['_layers'][l].setStyle({
				weight: 2,
				color: '#444',
				dashArray: ''
			});
		}

	}else{
		profilesMapActiveLayers[layer._leaflet_id] = layer.options;
		layer.setStyle({
			weight: 2,
			color: '#444',
			dashArray: ''
		});
	}

	if (!L.Browser.ie && !L.Browser.opera) {
		layer.bringToFront();
	}

}


ProfilesMap.prototype.unhighlightLayer = function(e){
	var layer = e.target;
	var id = layer._leaflet_id;
	// change the styleback
	layer.setStyle(profilesMapActiveLayers[id]);
	if (!L.Browser.ie && !L.Browser.opera) {
		layer.bringToBack();
	}
	delete profilesMapActiveLayers[id];
	
}

/*INFObox*/

ProfilesMap.prototype.makeInfoBox = function(className, defaultContent){
	/* Creates and returns and Infobox 
	 *
	 * <defaultContent> String
	 *
	 * */
	if(typeof(defaultContent)==='undefined'){
		defaultContent = '';
	}
	var info = L.control();
	
	// some info handlers
	info.onAdd = function(map){
		this._div = L.DomUtil.create('div', className); // create a div with a class "info"
		this.update();
		return this._div;
	}
	
	// method that we will use to update the control based on feature properties passed
	info.update = function (content) {
	    this._div.innerHTML = (content? content : defaultContent);
	};

	return info;
}

/*UTILS*/

ProfilesMap.prototype.getValueCodeFormat = function(value){
    /*Check for special instances of "codes"
     * -1 is always suppressed, 
     *  -999999 is always null data
     *
     * */

    if(value == null){
        value = -999999;
    }
    switch(value){
        case -999999:
        return "n/a"
    }

    return null;
}

ProfilesMap.prototype.formatCommafy = function(value, decimal){
    /*Put commas where they belong in a number*/
    var self = this;
    decimal = self.gOrd(decimal, false);
    if(decimal){
        value = value.toFixed(1) + '';
    }else{
        value = value.toString();
    }
    x = value.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    if(decimal){
        if(x2 == '.0') {
            return x1;
        } else {
            return x1 + x2;
        }
    }
    else{
        return x1;
    }
}

ProfilesMap.prototype.formatCount = function(value){
    var self = this;
    var v = self.getValueCodeFormat(value);
    if(v){
        return v
    }else{
        value = Math.round(value * 10 ) / 10;
        return self.formatCommafy(value, true);
    }
}

ProfilesMap.prototype.formatDollar = function(value){
    var self = this;
    var v = self.getValueCodeFormat(value);
    if(v){
        return v
    }else{
        return "$" + self.formatCommafy(value, false);
    }
}

ProfilesMap.prototype.formatPercent = function(value){
    var self = this;
    var v = self.getValueCodeFormat(value);
    if(v){
        return v
    }else{
        return self.formatCommafy(value, true)+"%";
    }
}

ProfilesMap.prototype.formatCustom = function(value, rules){
   // we kinda have to (py)reparse the comparison cause values maybe generated on the client as well.
   var self = this;
   var v = self.getValueCodeFormat(value);
   if(v){
        return v
   }else{
        for(var i in rules){
            var rule = rules[i];
            if(isNaN(parseFloat(rule.value_operator))){
                if(rule.display_value != -1 && value != 0){
                        var r = /[\d\<\>\=]+/;
                        if(r.test(rule.value_operator)){
                            if(eval(value+rule.value_operator)){
                                return rule.display_value;
                            }
                        }
                }else{
                    // supp val
                    return value.toString();
                }
            }else{
                // straight compare
                if(parseFloat(rule.value_operator) == parseFloat(value)){
                    return rule.display_value;
                }
            }
        }
        return value.toString();
   }
}

ProfilesMap.prototype.binEqInt = function(data, interval){
    /*Equal Interval spaced*/
    var interval = parseFloat(this.gOrd(interval, 10));

    var s = new geostats(data);
    var bins = [];
    var min = s.min();
    var max = s.max();
    while(min < max){
        bins.push(parseFloat(min.toFixed(2)));
        min += interval;
    }
    bins.push(max);
    return bins;
}

ProfilesMap.prototype.binJenks = function(data, num_bins){
    num_bins = parseFloat(this.gOrd(num_bins, 5));
    // lets clean out NaNs
    var clean_data = [];
    for(var i in data){
        if(!isNaN(data[i])){
            clean_data.push(data[i]);
        }
    }
    if(num_bins >= clean_data.length){
         num_bins = clean_data.length-1;
    }
  
    var s = new geostats(clean_data);
    var u = s.getUniqueValues();
    var f = new geostats(u);
    if(num_bins >= u.length){
        num_bins = u.length-1;
    }
    return f.getJenks(num_bins); 
}

ProfilesMap.prototype.binEqSpaced = function(data, num_bins){
    /*Equally spaced bins based on the data*/
    num_bins = this.gOrd(num_bins, 10);
    if(num_bins > data.length){
        num_bins = data.length-1;
    }
    var s = new geostats(data);
    var bins = [];
    var dist = s.max()-s.min(); // the difference between the max and the min
    var interval = dist/num_bins;
    var min = s.min();
    while(min < s.max()){
        bins.push(parseFloat(min.toFixed(2)));
        min += interval;
    }
    bins[bins.length-1] = s.max();
    return bins;
}

ProfilesMap.prototype.binCustomBreak = function(bin_list){
    /* a list of custom breaks from a string */
    bin_list = this.gOrd(bin_list, false);
    if(bin_list == false){
        throw "bin list is not defined"
    }else{
        bin_list = bin_list.replace(/\s/g, "");
        bin_list = bin_list.split(",");
    }
    return bin_list.map(function(a){return parseFloat(a)})
}

ProfilesMap.prototype.binAll = function(data){
    /* Returns a list of unique values found in data*/
    var s = new geostats(data);
    return s.getUniqueValues();
}

ProfilesMap.prototype.inBin = function(value, bin){
    /* Return True if value is in bin 
     * if bin.values is an array bin ex: [1, 10] we will check if value meets that range
     * if bin.values is a single value we will do a == comparison
     * */
    var result = false;
    value = parseFloat(value);
    if(bin.values.length == 2){
        // Lets make sure that bin is always sorted min-max
        bin.values = bin.values.sort(function(a,b){
            return a-b;
        });
        result = value >= bin.values[0] && value <=bin.values[1]; 
    }else if(bin.values.length == 1){
        result = value == bin.values[0];
    }
    return result;
}

ProfilesMap.prototype.makeBins = function(num_array, min_max){
    /* create an array of bins from an array of nums*/
    var self = this;
    var bins = [];
    var vals;
    min_max = self.gOrd(min_max, true); // should we save this in a[min, max] array?
    if(min_max){
        for(var i = 0; i< num_array.length-1; i++){
            // we need to seperate some numbers since they may be more interesting on thier own instead of being grouped.
            if((num_array[i] - num_array[i+1]) * -1 > .01 && self.getValueCodeFormat(num_array[i])==null){
                vals = [num_array[i], num_array[i+1]];
                vals = vals.sort(function(a,b){return a-b;});
                bins.push({'values': vals,'color': self.colorList[i]});
            }else{
                bins.push({'values': [num_array[i]], 'color' : self.colorList[i]});
            }
        }
    }else{
        for(var i = 0; i< num_array.length; i++){
            bins.push({'values':[num_array[i]], 'color' :self.colorList[i]})
        }

    }


    return bins;
}


ProfilesMap.prototype.gOrd = function(var_name, default_val){
    /* default vars in functions */
    if(typeof(var_name) ==='undefined' || var_name==null) var_name = default_val;
    return var_name;    
}

ProfilesMap.prototype.getColor = function(value, bins){
	/**
     * iterate list of bins and return a color from self.colorlist
	 */
    var self = this;
	var color;
    var bin;
	value = parseFloat(value);
	for(var i =0; i<bins.length; i++){
        bin = bins[i];
		if(self.inBin(value, bin)){
			color = bin.color; // the last element in the bin is always he hex color
		}
	}

	return color;
} 

	 
/*Zoom manager*/

ProfilesMap.prototype.updateLayers = function(currentZoomLevel){
	var self = this;
	var layer;
	var threshold; // the threshold set to the managedLayer
	var layerCtrl;
	var name;
	var czl = currentZoomLevel; //map should pass this to us
	for(var i in self.managedLayers){

		layer = self.managedLayers[i].layer;
		threshold = self.managedLayers[i].zoomThreshold;
		if(self.managedLayers[i].hasOwnProperty('layerControl')){
		       	layerCtrl = self.managedLayers[i].layerControl;
			name = self.managedLayers[i].layerName;
		}

		if(threshold <= czl){
			// show the layer
			// lets check to see if the map has the layer already
			var checked = $("input.leaflet-control-layers-selector:checked").parent().children('span').text();
			if(!self.map.hasLayer(layer)){
				// but only if its checked in the checkbox 
				if(checked.indexOf(name)!==-1){
					self.map.addLayer(layer);
					// take this out of the layer control if it has one.
				}

				if(layerCtrl) layerCtrl.addOverlay(layer, name);
			}
		}else{
			// get rid of the layer
			if(self.map.hasLayer(layer)){
				self.map.removeLayer(layer);	
				if(layerCtrl) layerCtrl.removeLayer(layer);

			}
		}

	}
}

ProfilesMap.prototype.valid_moe = function(value_obj){
	if(parseFloat(value_obj['number']) < parseFloat(value_obj['moe'])){
		return false;
	}else{
		return true;
	}
	
}

/**
* geostats() is a tiny and standalone javascript library for classification 
* Project page - https://github.com/simogeo/geostats
* Copyright (c) 2011 Simon Georget, http://valums.com
* Licensed under the MIT license
*/
/*
 * 
 *
 * */
var _t=function(h){return h},inArray=function(h,a){for(var b=0;b<a.length;b++)if(a[b]==h)return!0;return!1},geostats=function(h){this.legendSeparator=this.separator=" - ";this.method="";this.roundlength=2;this.is_uniqueValues=!1;this.bounds=[];this.ranges=[];this.colors=[];this.counter=[];this.stat_cov=this.stat_stddev=this.stat_variance=this.stat_pop=this.stat_min=this.stat_max=this.stat_sum=this.stat_median=this.stat_mean=this.stat_sorted=null;this.serie="undefined"!==typeof h&&0<h.length?h:[];
this.setSerie=function(a){this.serie=[];this.serie=a};this.setColors=function(a){this.colors=a};this.doCount=function(){if(!this._nodata()){var a=this.sorted();for(i=0;i<this.bounds.length;i++)this.counter[i]=0;for(j=0;j<a.length;j++){var b=this.getClass(a[j]);this.counter[b]++}}};this.setRanges=function(){this.ranges=[];for(i=0;i<this.bounds.length-1;i++)this.ranges[i]=this.bounds[i]+this.separator+this.bounds[i+1]};this.min=function(){if(!this._nodata())return this.stat_min=Math.min.apply(null,
this.serie)};this.max=function(){return this.stat_max=Math.max.apply(null,this.serie)};this.sum=function(){if(!this._nodata()){if(null==this.stat_sum)for(i=this.stat_sum=0;i<this.pop();i++)this.stat_sum+=this.serie[i];return this.stat_sum}};this.pop=function(){if(!this._nodata())return null==this.stat_pop&&(this.stat_pop=this.serie.length),this.stat_pop};this.mean=function(){if(!this._nodata())return null==this.stat_mean&&(this.stat_mean=this.sum()/this.pop()),this.stat_mean};this.median=function(){if(!this._nodata()){if(null==
this.stat_median){this.stat_median=0;var a=this.sorted();this.stat_median=a.length%2?a[Math.ceil(a.length/2)-1]:(a[a.length/2-1]+a[a.length/2])/2}return this.stat_median}};this.variance=function(){round="undefined"===typeof round?!0:!1;if(!this._nodata()){if(null==this.stat_variance){for(var a=0,b=0;b<this.pop();b++)a+=Math.pow(this.serie[b]-this.mean(),2);this.stat_variance=a/this.pop();!0==round&&(this.stat_variance=Math.round(this.stat_variance*Math.pow(10,this.roundlength))/Math.pow(10,this.roundlength))}return this.stat_variance}};
this.stddev=function(a){a="undefined"===typeof a?!0:!1;if(!this._nodata())return null==this.stat_stddev&&(this.stat_stddev=Math.sqrt(this.variance()),!0==a&&(this.stat_stddev=Math.round(this.stat_stddev*Math.pow(10,this.roundlength))/Math.pow(10,this.roundlength))),this.stat_stddev};this.cov=function(a){a="undefined"===typeof a?!0:!1;if(!this._nodata())return null==this.stat_cov&&(this.stat_cov=this.stddev()/this.mean(),!0==a&&(this.stat_cov=Math.round(this.stat_cov*Math.pow(10,this.roundlength))/
Math.pow(10,this.roundlength))),this.stat_cov};this._nodata=function(){return 0==this.serie.length?(alert("Error. You should first enter a serie!"),1):0};this.sorted=function(){null==this.stat_sorted&&(this.stat_sorted=!1==this.is_uniqueValues?this.serie.sort(function(a,b){return a-b}):this.serie.sort(function(a,b){var c=a.toString().toLowerCase(),d=b.toString().toLowerCase();return c<d?-1:c>d?1:0}));return this.stat_sorted};this.info=function(){if(!this._nodata()){var a;a=""+(_t("Population")+" : "+
this.pop()+" - ["+_t("Min")+" : "+this.min()+" | "+_t("Max")+" : "+this.max()+"]\n");a+=_t("Mean")+" : "+this.mean()+" - "+_t("Median")+" : "+this.median()+"\n";return a+=_t("Variance")+" : "+this.variance()+" - "+_t("Standard deviation")+" : "+this.stddev()+" - "+_t("Coefficient of variation")+" : "+this.cov()+"\n"}};this.getEqInterval=function(a){if(!this._nodata()){this.method=_t("eq. intervals")+" ("+a+" "+_t("classes")+")";var b=this.max(),c=[],d=this.min(),e=(b-this.min())/a;for(i=0;i<=a;i++)c[i]=
d,d+=e;c[a]=b;this.bounds=c;this.setRanges();return c}};this.getQuantile=function(a){if(!this._nodata()){this.method=_t("quantile")+" ("+a+" "+_t("classes")+")";var b=[],c=this.sorted(),d=Math.round(this.pop()/a),e=d,f=0;b[0]=c[0];for(f=1;f<a;f++)b[f]=c[e],e+=d;b.push(c[c.length-1]);this.bounds=b;this.setRanges();return b}};this.getJenks=function(a){if(!this._nodata()){this.method=_t("Jenks")+" ("+a+" "+_t("classes")+")";dataList=this.sorted();for(var b=[],c=0,d=dataList.length+1;c<d;c++){for(var e=
[],f=0,k=a+1;f<k;f++)e.push(0);b.push(e)}c=[];d=0;for(e=dataList.length+1;d<e;d++){for(var f=[],k=0,h=a+1;k<h;k++)f.push(0);c.push(f)}d=1;for(e=a+1;d<e;d++){b[0][d]=1;c[0][d]=0;for(var g=1,f=dataList.length+1;g<f;g++)c[g][d]=Infinity;g=0}d=2;for(e=dataList.length+1;d<e;d++){for(var h=k=f=0,m=1,q=d+1;m<q;m++){var n=d-m+1,g=parseFloat(dataList[n-1]),k=k+g*g,f=f+g,h=h+1,g=k-f*f/h,p=n-1;if(0!=p)for(var l=2,r=a+1;l<r;l++)c[d][l]>=g+c[p][l-1]&&(b[d][l]=n,c[d][l]=g+c[p][l-1])}b[d][1]=1;c[d][1]=g}g=dataList.length;
c=[];d=0;for(e=a+1;d<e;d++)c.push(0);c[a]=parseFloat(dataList[dataList.length-1]);for(c[0]=parseFloat(dataList[0]);2<=a;)d=parseInt(b[g][a]-2),c[a-1]=dataList[d],g=parseInt(b[g][a]-1),a-=1;c[0]==c[1]&&(c[0]=0);this.bounds=c;this.setRanges();return c}};this.getUniqueValues=function(){if(!this._nodata()){this.method=_t("unique values");this.is_uniqueValues=!0;var a=this.sorted(),b=[];for(i=0;i<this.pop();i++)inArray(a[i],b)||b.push(a[i]);return this.bounds=b}};this.getClass=function(a){for(i=0;i<this.bounds.length;i++)if(!0==
this.is_uniqueValues){if(a==this.bounds[i])return i}else if(a<=this.bounds[i+1])return i;return _t("Unable to get value's class.")};this.getRanges=function(){return this.ranges};this.getRangeNum=function(a){var b,c;for(c=0;c<this.ranges.length;c++)if(b=this.ranges[c].split(/ - /),a<=parseFloat(b[1]))return c};this.getHtmlLegend=function(a,b,c,d){var e="";ccolors=null!=a?a:this.colors;lg=null!=b?b:"Legend";null!=c?(this.doCount(),getcounter=!0):getcounter=!1;fn=null!=d?d:function(a){return a};if(ccolors.length<
this.ranges.length)alert(_t("The number of colors should fit the number of ranges. Exit!"));else{a='<div class="geostats-legend"><div class="geostats-legend-title">'+_t(lg)+"</div>";if(!1==this.is_uniqueValues)for(i=0;i<this.ranges.length;i++)!0===getcounter&&(e=' <span class="geostats-legend-counter">('+this.counter[i]+")</span>"),-1!=this.ranges[i].indexOf(this.separator)?(b=this.ranges[i].split(this.separator),b=fn(b[0])+this.legendSeparator+fn(b[1])):b=fn(this.ranges[i]),a+='<div><div class="geostats-legend-block" style="background-color:'+
ccolors[i]+'"></div> '+b+e+"</div>";else for(i=0;i<this.bounds.length;i++)!0===getcounter&&(e=' <span class="geostats-legend-counter">('+this.counter[i]+")</span>"),b=fn(this.bounds[i]),a+='<div><div class="geostats-legend-block" style="background-color:'+ccolors[i]+'"></div> '+b+e+"</div>";return a+"</div>"}};this.getSortedlist=function(){return this.sorted().join(", ")}};


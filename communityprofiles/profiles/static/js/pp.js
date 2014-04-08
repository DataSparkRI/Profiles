/*
 * COMMON Provplan JS
 * Requires JQuery
 *
 *
 **/
var PP = PP || {}; // the provplan namespace

PP.Settings = {
	baseURL:'',
	apiVersion:'v1'
}

extend(PP, {
	XHR:{
		getCachedItem:function(cacheKey){
			/*
			cacheKey = PP.Utils.createHash(cacheKey);
			if(localStorage[cacheKey]){
				return JSON.parse(localStorage[cacheKey]);
			}else{
				return false;
			}*/
			/*LOCAL STORAGE IS DISABLED RIGHT NOW*/
			return false
		},

		setCachedItem:function(cacheKey, data){
			cacheKey = PP.Utils.createHash(cacheKey);
			try{
				localStorage[cacheKey] = JSON.stringify(data);
			} catch(e){
				if(e.name === 'QUOTA_EXCEEDED_ERR') {
					localStorage.clear();
					localStorage[cacheKey] = JSON.stringify(data);
				}
			}
		},

		fetchData:function(dataURL, cachable, cacheKey, callback){
			var self = this;
			// check if this in the cache
			var data = self.getCachedItem(cacheKey);
			if(data){
				if(typeof(callback)!=='undefined'){
					callback(data);	
				}	
				return true;
			}else{
				$.getJSON(dataURL, function(data){	
					// update the cache
					if(cachable) self.setCachedItem(cacheKey, data);
					if(typeof(callback)!=='undefined'){
						callback(data);	
					}	
				});
			}

		},

		getIndicatorData: function(indicator_ids, geography_ids, cachable, callback){
			/* Given a list of indicator_ids(slugs), geogrpahy_ids or slugs, 
			 * Returns data from profiles api
			 * EX: http://0.0.0.0:8555/api/v1/ind/?slug__in=income6&geo=providence&format=json
			 * */
			var self = this; // refers to XHR
			var dataURL = PP.Settings.baseURL + "/api/" + PP.Settings.apiVersion + "/ind/?slug__in="+indicator_ids.toString() +"&" +PP.Utils.buildQueryString("geo", geography_ids) + "&format=json";
			
			if(typeof(cachable)==='undefined' || cachable===null) cachable = true;

			var cacheKey = indicator_ids.toString()+"-"+geography_ids.toString();

			self.fetchData(dataURL, cachable, cacheKey, callback);
			
		},
		
		getGeoData: function(geography_ids, dataQ, cachable, callback){
			/**
			 * Fetches Geography data from the Profiles Map Api.
			 * Along with GeoJSON data, the API supports fetching Indicator data via additional GET params. Pass them via the dataQ param
			 *
			 * @method getGeoData
			 * @param {Array} geography_ids A list of valid GeoRecord Slugs. Ex: [providence, cranston]
			 * @param {String} dataQ a formated query string that may contain: <ind=slug> <denom=DenominatorName> <time=TimeName> OR <change=true> EX: &ind=income6&time=2000&denom=% of Population
			 * @param {Boolean} cachable If true, will look in the PP.XHR.cache before actually doing the request.
			 * @param {Function} callback A function that should get executed with the XHR request completes. It gets passed <data>.
			 *
			 */
			var self = this;
			/*-- DEFAULT VALUES---*/
					
			if(typeof(dataQ)==='undefined'|| dataQ===null) dataQ = '';
			if(typeof(cachable)==='undefined' || cachable===null) cachable = true;
			
			dataQ = dataQ.replace(/&&/g,"");
			var dataURL = PP.Settings.baseURL + "/maps_api/" + PP.Settings.apiVersion + "/geo/?slug__in="+geography_ids.toString();
			dataURL += "&" + dataQ;
		       	dataURL += "&format=json&limit=0";
			dataURL = dataURL.replace(/&&/g,"");
			
			var cacheKey = geography_ids.toString()+dataQ;
			self.fetchData(dataURL, cachable, cacheKey, callback);

		}, 
		getGeoDataById: function(geography_ids, dataQ, cachable, callback){
			/**
			 * Fetches Geography data from the Profiles Map Api by ID. 
			 * Along with GeoJSON data, the API supports fetching Indicator data via additional GET params. Pass them via the dataQ param
			 *
			 * @method getGeoData
			 * @param {Array} geography_ids A list of valid GeoRecord Ids
			 * @param {String} dataQ a formated query string that may contain: <ind=slug> <denom=DenominatorName> <time=TimeName> OR <change=true> EX: &ind=income6&time=2000&denom=% of Population
			 * @param {Boolean} cachable If true, will look in the PP.XHR.cache before actually doing the request.
			 * @param {Function} callback A function that should get executed with the XHR request completes. It gets passed <data>.
			 *
			 */
			var self = this;
			/*-- DEFAULT VALUES---*/
					
			if(typeof(dataQ)==='undefined'|| dataQ===null) dataQ = '';
			if(typeof(cachable)==='undefined'|| cachable===null) cachable = true;

			dataQ = dataQ.replace(/&&/g,"");
			var dataURL = PP.Settings.baseURL + "/maps_api/" + PP.Settings.apiVersion + "/geo/set/"+ geography_ids.join(";")+"/?";
			dataURL += "&" + dataQ;
		    dataURL += "&format=json&limit=0";
			dataURL = dataURL.replace(/&&/g,"");
			
			var cacheKey = geography_ids.toString()+dataQ;
			self.fetchData(dataURL, cachable, cacheKey, callback);

		}, 
		getGeoDataByIdV2: function(geography_ids, cachable, callback){
			/*-- DEFAULT VALUES---*/
		    var self = this;
			if(typeof(cachable)==='undefined'|| cachable===null) cachable = true;
            var dataURL = API_URL + "/shp/?geos=";
            dataURL += geography_ids.join();
			var cacheKey = geography_ids.toString()+"V2-shp";
			self.fetchData(dataURL, cachable, cacheKey, callback);

		}, 
		
		getChunkedGeoData: function(geography_ids, dataQ, cachable, callback){
			/**
			 * Does multiple request to API.
			 *
			 */
			var self = this;
			var total_objs = geography_ids.length;
			var loaded_count = 0;
			var pool = [];

			if(typeof(dataQ)==='undefined'|| dataQ===null) dataQ = '';
			dataQ = dataQ.replace(/&&/g,"");

			var cacheKey = geography_ids.toString()+dataQ;
			// check if this in the cache
			var data = self.getCachedItem(cacheKey);

			if(data){
				if(typeof(callback)!=='undefined'){
					callback(data);	
				}	
				return true;
			}else{
				for(var g in geography_ids){
					self.getGeoData(geography_ids[g], dataQ, false, function(data){
						pool.push(data.objects[0]);
						loaded_count++;
						if(loaded_count===total_objs){	
							if(cachable) self.setCachedItem(cacheKey, {'objects':pool});
							if(typeof(callback)!=='undefined'){
								callback({'objects':pool});	
							}	
						}
					});

				}
			}

		},

		getMapFeatureData: function(type, feature_set, cachable, callback){
			/**
			 * Fetches Map Feature data set from maps api
			 * @param {String} type Should be <line> or <point> or <poly>
			 * @param {String} feature_set Ex: <1;2;3>
			 */
			var self = this;
			var dataURL = PP.Settings.baseURL + "/maps_api/" + PP.Settings.apiVersion;
			dataURL += "/" + type + "_feat/set/";
			dataURL += feature_set;
			dataURL += "/?format=json";

			if(typeof(cachable)==='undefined'|| cachable===null) cachable = true;

			var cacheKey = type + "-" + feature_set;
			self.fetchData(dataURL, cachable, cacheKey, callback);

		},
		
		geoCodeAddress: function(street, city, zip, callback){
			var self = this;
			var dataURL = PP.Settings.baseURL + "/maps_api/" + PP.Settings.apiVersion;
			dataURL+= "/geocode/?";

			if(typeof(street) ==='undefined' || street ===null) street = '';
			if(typeof(city)==='undefined' || city===null) city = '';
			if(typeof(zip)==='undefined' || zip===null) zip = '';

			dataURL+= "street=" + street;
			dataURL+= "&city=" + city;
			dataURL += "&zip=" + zip;
			dataURL += "&format=json";

			var cacheKey = street+city+zip;
			self.fetchData(dataURL, true, cacheKey, function(d){
				if(typeof(callback)!=='undefined'){

					callback(d['objects'][0]);
				}

				
			});

		}
	},
	
	Utils:{
		buildQueryString:function(prefix, array){
			/*
			* Build a url from an array or items. ex:
			* prefix = myParam;
			* array = [1,2,3] ;
			* returns myParam=1&myParam=2&myParam=3
			* */
			var self = this;
			var out = "";
			if(array.length !==0){
				out += prefix+"=";
				out += array.join("&"+prefix+"=");
			}
			return out;

		},

		timeSort: function(a,b){
			/**
			 * Used to sort Profiles Time Names.
			 * EX: 
			 * times = ['2000','2010','2006 - 2010'];
			 * times.sort(PP.Utils.timeSort);
			 */
			a = a.replace(/ /g,'');
			a = a.split('-');
			a = a[a.length-1];
			b = b.replace(/ /g,'');
			b = b.split('-');
			b = b[b.length-1]
			return b-a;
		},

		createHash: function(str){
			var hash = 0, i, char;
			if (str.length == 0) return hash;
			for (i = 0; i < str.length; i++) {
				char = str.charCodeAt(i);
				hash = ((hash<<5)-hash)+char;
				hash = hash & hash; // Convert to 32bit integer
			}
			return hash;
		},

        getObjKeys: function(obj){
            var keys = [];
            for(var key in obj){
                keys.push(key)
            }
            return keys;
        },
        
        uniqueArray:function(arr){
           var u = {}, a = [];
           for(var i = 0; i < arr.length; i++){
              if(u.hasOwnProperty(arr[i])) {
                 continue;
              }
              a.push(arr[i]);
              u[arr[i]] = null;
           } 

            return a;
        }

	}
	
});

/*===============OS utils============================================*/

// extend.js
// written by andrew dupont, optimized by addy osmani
function extend(destination, source) {
    var toString = Object.prototype.toString,
        objTest = toString.call({});
    for (var property in source) {
        if (source[property] && objTest == toString.call(source[property])) {
            destination[property] = destination[property] || {};
            extend(destination[property], source[property]);
        } else {
            destination[property] = source[property];
        }
    }
    return destination;
};

/*GEOSTATS*/
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


var app = angular.module("profiles", ['ngSanitize', 'ngStorage']).

config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
})

app.service('launchDataview', function(){
    return function(event, $scope){
        event.preventDefault();
        //$scope.dataViewActive = true;
        var el = $(event.target);
        var url = el.attr("href");
        if(!angular.isUndefined($scope.level)){
            url += "#" + $scope.level.slug;
        }
        var wW = $(window).width();
        var wH = $(window).height();
        var tH = wH -(wH *.25);
        
      
        $("#dataview-modal .modal-body").css({
            height:tH
        });


        if(angular.isUndefined($scope.init_record)){
            $("#dataview-modal .modal-title").text($scope.indicator.name);
        }else{
            $("#dataview-modal .modal-title").text(el.data('indicator') + " - " + $scope.init_record.name);
        }
        $("#dataview-modal iframe").attr("src", url);
        $('#dataview-modal').modal('show');
    } 

});

app.filter('safehtml', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});

app.filter('col', function() {
    return function(val) {
        val = parseInt(val);
        return val == 1 ? 2 : 1;
    };
});

app.filter('prefix', function(){
    return function(val, prefix) {
        if(!angular.isUndefined(val)){
            return prefix + " " + val;
        }
        return val;
    }
});

app.filter('ifBool', function(){
    /*Check a bool and spit something out*/
    return function(bool, out){
        if(bool){
            return out;
        }
    } 
});

app.filter('roundDecimal', function(){
    return function(val){
        if(val == "n/a") return val;
        val = parseFloat(val);
        
        if(val % 1 !== 0){
            d = Math.round( val * 10 ) / 10;
            return d;  
        }
        return val;
    }
});

function MapCntrl($scope, $http, $sanitize, $compile, $timeout, $q, $log, $location, $window, $localStorage, launchDataview){
    $scope.levels = null;
    $scope.level = null;
    $scope.init_level = null;
    $scope.records = []; // a placeholder to found records
    $scope.filter_key;
    $scope.census_id;
    $scope.options_records = []; // records that can be selected by user
    $scope.lev_records = []; // records that are like the initial level records
    $scope.init_record = null;
    $scope.active_record = null;
    $scope.geoms = [];
    $scope.base_map = null;
    $scope.linkage = {};
    $scope.domain = {};
    $scope.address;
    $scope.data_cache = {};
    $scope.enabled_times = [];
    $scope.$storage = $localStorage.$default({levelstate:null})
    $scope.predicate = 'label';

    $scope.onGeoRollover = function(e){
        var l = e.target;
        var props = l.feature.geometry.properties;
        
        $scope.pm.infoBox.update('<h4>'+props.label+'</h4>');
        $scope.pm.highlightLayer(e);
    }

    $scope.onGeoRollout = function(e){
        var layer = e.target;
        var props = layer.feature.geometry.properties;
        $scope.pm.unhighlightLayer(e);
        $scope.pm.infoBox.update();
    }

    $scope.onGeoClick = function(e){
        var layer = e.target;
        var props = layer.feature.geometry.properties;
        $timeout(function(){
            $scope.navigateTo($scope.level.slug, props.slug, $scope.domain.slug);
        }, 20);
    }

    $scope.geoQuery = function(recordObj, rLevel, tLevel, callback){
        /*Find Records that contain recordObj || records that are in recordObj and are at targe level*/
        var q;
        var p;
        // if the sum level of the target level is larger than the recordLevel then we assume its "IN" query
        if(parseInt(tLevel.sumlev) > parseInt(rLevel.sumlev)){ // this is making assumptions that sumlevs will always follow the census' pattern
            q = "IN";
        }else{
            q = "OF";
        }

        p = $http.get($scope.api_url + '/shp/q/', {params:{ geoms:recordObj.geom_id, lev:tLevel.id, q:q}})
        .success(function(data, status, headers, config){
            callback(data, tLevel);
        });

        return p;

    }

    $scope.onLevChange = function(updateTS){
        if(updateTS == true){
            var now = Date.now()
            $scope.$storage.levelstate = { 
                level: $scope.level,
                time: now
            } // keep track of the level state as it changes
        }
        // fetch geometry records that are at the selected level and are in or contain our current Record
        $scope.geoQuery($scope.init_record, $scope.init_level, $scope.level, function(data){
            if(data.objects.length == 1){
                $scope.selected_record = data.objects[0];
                $scope.updateRecord();
                return true
            }

            if(data.objects.length != 0){
                $scope.records = data.objects; // records are the geoms that comeback
                try{
                    // remove geoms on map if there are any.
                    $scope.pm.map.removeLayer($scope.base_map);
                }catch(e){
                    //...
                }
                if(angular.isUndefined($scope.indicator)){
                    $scope.getGeoms();
                    $scope.options_records = data.objects;
                    $("#geo-level-recs-wrap").removeClass("hidden");
                }

            }else{
                $("#geo-level-recs-wrap").addClass("hidden");
            }
        });
    };

    $scope.getGeoms = function(){
        /* Retrieve geom polygons by geos ids and updates MAP*/
        var geomIdList = [];
        for(var i in $scope.records){
            geomIdList.push($scope.records[i].id);
        }
        if(geomIdList != null && geomIdList.length > 0){
            $http.get($scope.api_url + "/shp/", {params:{geos:geomIdList.join()}})
            .success(function(data, status, headers, config){
                $scope.base_map = $scope.pm.DataPolyFeatureGroup(data, null, {
                    mouseover: $scope.onGeoRollover,
                    mouseout: $scope.onGeoRollout,
                    click: $scope.onGeoClick
                });
                $scope.base_map.addTo($scope.pm.map);
                $scope.pm.map.fitBounds($scope.base_map.getBounds());

            })
            .error(function(data, status, headers, config) {
            });
        }
    }

    $scope.getRecordsByLev = function(levSlug, updateLevRecs, callback) {
        /*Return a list of Records at a specified Level*/
        if(angular.isUndefined(updateLevRecs)){
            updateLevRecs = false;
        }
        $http.get($scope.api_url + '/geos/level/'+levSlug, {params:{filter:$scope.filter_key}})
        .success(function (data, status, headers, config){
            $scope.linkage[levSlug] = {};
            var rec;
            var lr = [];
            for(var i in data.objects){
                rec = data.objects[i];
                if(updateLevRecs){
                    if(rec.slug != $scope.init_record.slug){
                        lr.push(rec);
                    }
                }
                $scope.linkage[levSlug][rec.geoKey] = rec;
            }
            if(updateLevRecs){
                $scope.lev_records = lr;
                if(lr.length>0){
               $scope.geoms = [];
                    $("#similar-nav").show();
                }else{
                    $("#similar-nav").hide();
                }
            }

            if(!angular.isUndefined(callback)){
                callback(levSlug);
            }
        });
        
    }
    $scope.getLevelFromSlug = function(slug){
        /*Get Level object from its slug*/
        for(var i in $scope.levels){
            if($scope.levels[i].slug == slug){
                return i;
            }
        }

        return false;
    }

    $scope.updateLev = function(level, updateTS){
        console.log(level)
        if(angular.isUndefined(updateTS)){ updateTS = false; }
        $scope.level = level;
        $scope.onLevChange(updateTS);
    }
      
    $scope.getLinkedRec = function(levSlug, geoKey){
        return $scope.linkage[levSlug][parseInt(geoKey)]
    }

    $scope.groupSelect = function(inds, group_name, event){
        /*fired when the group is expanded
         *TODO: caching
         * */

        var u = {}; // year combo look up
        var targ = $(event.target).parent().parent(); // the containing li
        var panel = targ.parent().parent().parent()
        var t, th, tr, td, tm, tb, indtr = null;
        var el = $(event.target);
        var yc;
        var colspan = 1;
        var indicators = {};

        if(!el.hasClass("title")){
            el = $(el.parent());
            targ = el.parent().parent();
        }
        event.preventDefault();

        el.toggleClass("expanded");
        el.find(".glyphicon").toggleClass("glyphicon-chevron-down");

        if(!targ.hasClass("fetched")){
            targ.children('table').removeClass('hidden');
            event.stopPropagation();
            //add a new group memeber to the datacache
            $scope.data_cache[group_name] = {'indicators':{}, 'denoms':[], 'groupedTimes':{}};
            for(var i in inds){
                var proms = [];
                var denoms = {};
                
                if(!indicators.hasOwnProperty(inds[i].slug)){
                    indicators[inds[i].slug] = inds[i];
                    indicators[inds[i].slug]['vals'] = {};
                    var b = $('body');
                    indicators[inds[i].slug].denominators = [];
                }

                // denoms
                for(var d in inds[i].denoms){
                    if(!denoms.hasOwnProperty(inds[i].denoms[d].slug)){
                        denoms[inds[i].denoms[d].slug] = inds[i].denoms[d];
                        denoms[inds[i].denoms[d].slug].vals = {};
                    }
                }

                indicators[inds[i].slug]['targ_url'] = "//" + $scope.app_url + "/profiles/dataview/"+$scope.init_level.slug+"/"+$scope.init_record.slug+"/"+inds[i].slug;
                if(!angular.isUndefined(window.AUTHN)){
                    indicators[inds[i].slug]['alink'] = '<a class="admin-link hidden-print" target="blank" href="/admin/profiles/indicator/'+ inds[i].id +'">EDIT</a>';   
                }

                for(var k in inds[i].times){
                    var p = $http.get($scope.api_url + '/indicator/'+inds[i].slug, 
                            {
                            params:{
                                geos:$scope.init_record.id, 
                                time:inds[i].times[k],
                                slg:inds[i].slug,
                                t:"i",
                            },
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                    });
                    proms.push(p);

                    // also grab any denoms
                    for(var d in inds[i].denoms){
                        denoms[inds[i].denoms[d].slug]['targ_url'] = "//" + $scope.app_url + "/profiles/dataview/"+$scope.init_level.slug+"/"+$scope.init_record.slug+"/"+inds[i].denoms[d].slug + "/?d=t";
                        var p = $http.get($scope.api_url + '/indicator/'+inds[i].denoms[d].slug, 
                                {
                                    params:{
                                         geos:$scope.init_record.id, 
                                         time:inds[i].times[k],
                                         slg:inds[i].denoms[d].slug,
                                         t:"d",
                                        },
                                 headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                        });
                    
                        proms.push(p);
                    }
                    indicators[inds[i].slug].denominators = denoms;
                    
                }  

                $q.all(proms).then(function(results){
                    /*at this point all of this indicator's data has come back including denoms*/
                    var p;
                    var k;
                    var times = []
                    for(var i in results){
                        p = results[i].config.params;
                        if(p.t == "i"){
                            k = p.slg; // always use the ind slug as the authoriative key
                            times.push(p.time);
                            try{
                                try{
                                    indicators[p.slg]['vals'][p.time] = {value:results[i].data.objects[0].f_number, moe:$scope.moe(results[i].data.objects[0].moe), type:index[results[i].data.objects[0].indicator_slug], integer:parseInt(results[i].data.objects[0].f_number.replace(/\,/g,''))};}
                                catch(e){indicators[p.slg]['vals'][p.time] = {value:results[i].data.objects[0].f_number, moe:$scope.moe(results[i].data.objects[0].moe), integer:parseInt(results[i].data.objects[0].f_number.replace(/\,/g,''))};}
                            }catch(e){
                                indicators[p.slg]['vals'][p.time] = {value:"-", moe: null};
                            }
                        }else{
                            /*denom*/
                            try{

                                indicators[k].denominators[p.slg]['vals'][p.time] = {
                                    value: results[i].data.objects[0].f_percent,

                                    moe:$scope.moe(results[i].data.objects[0].moe === null ? null :results[i].data.objects[0].moe, "%"),

                                    number:results[i].data.objects[0].f_number
                                };
                            }catch(e){
                                indicators[k].denominators[p.slg]['vals'][p.time] = {value:"-", moe:$scope.moe(null), count:"-"};
                            }
                        }
                       
                    }
                    if(!$scope.data_cache[group_name].groupedTimes.hasOwnProperty(times.join("&"))){
                        $scope.data_cache[group_name].groupedTimes[times.join("&")] = {times:times, indicators:[]};
                    }
                    $scope.data_cache[group_name].sortedGroupedTimes = $scope.objKeys($scope.data_cache[group_name].groupedTimes).sort(function(a,b){
                        var aC = parseInt(a.replace("&", ""));
                        var bC = parseInt(b.replace("&", ""));
                        return aC > bC;
                    });

                    $scope.data_cache[group_name].groupedTimes[times.join("&")].indicators.push(indicators[k]);
                });
               
            } // end for i in inds
            
            
            $timeout(function(){
                targ.find('.moe').tooltip({delay:{show:10, hide:10}});
                targ.find('.denominator').tooltip({delay:{show:10, hide:10}});

            }, 200);

            el.click(function(){
                targ.children("table").toggle();
            });
            targ.addClass("fetched");
                        
        }// end if !targ.hasClass("fetched")

    }

    $scope.moe = function(value, appendTxt){
        if(angular.isUndefined(appendTxt)){appendTxt =""};
        if(value != null){
            value = $scope.pm.formatCommafy(parseFloat(value)); // TODO: There are all sorts of places where these numbers are getting rounded. This is inconsistent and BAD.
            var el = '<a href="#" class="moe" data-toggle="tooltip" title ="+/-&nbsp;'+ value + appendTxt +'">+/-</a>';
            return el;
        }
        return '';
    }

    $scope.navigateTo = function(levelSlug, recordSlug, domainSlug){
        /*Navigate to a new location*/
        var url = "//" + $scope.app_url + "/profiles/" + levelSlug + "/" + recordSlug + "/" + domainSlug + "/";
        window.location.href = url;
    }

    $scope.bcrumbNav = function(event){
        
    }

    $scope.updateRecord = function(recordSlug, levelSlug){
        if(angular.isUndefined(recordSlug)){
            // default behavior
            $scope.navigateTo($scope.level.slug, $scope.selected_record.slug, $scope.domain.slug);
        }else{
            $scope.navigateTo(levelSlug, recordSlug, $scope.domain.slug);
        }
    }

    $scope.updateRecordFromSimilar = function(){
        $scope.updateRecord($scope.selected_record.slug, $scope.init_level.slug, $scope.domain.slug);
    }

    $scope.geocodeAddress = function(){
        if (angular.isUndefined($scope.address)){
            $scope.geocode_mssg = "Street is Required.";
            $scope.geocode_mssg_type = "danger";
            return false;
        }
        $scope.selected_address = null;
        var pAddr = $scope.address.split(",");
        var st = pAddr[0] || null;
        var city = pAddr[1] || "";
        var zip = pAddr[2] || "";
        
        if(st != null){
            $http.get("//" + $scope.app_url + "/" + "maps_api/v1/geocode/", {params:{street:st, city:city, zipcode:zip}})
            .success(function (data, status, headers, config){
                if(data.objects[0].status == "success"){
                    $scope.geocode_mssg = "Found " + data.objects[0].results.length + " Results";
                    $scope.geocode_mssg_type = "info";

                    $scope.addr_results = data.objects[0].results;

                }else{
                    $scope.geocode_mssg = "Sorry, we couldnt find that address";
                    $scope.geocode_mssg_type = "default";
                }
            });
        }else{
            $scope.geocode_mssg = "Street is Required.";
            $scope.geocode_mssg_type = "danger";

            return false;
        }
    }

    $scope.chooseAddress = function(addr, $event){
        $event.preventDefault();
        $scope.$storage.levelstate = null; // we need to wipe out the levelstate
        $scope.geocode_mssg = "";
        $scope.addr_results = []; 
        addr.location.address = addr.location.address.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
        addr.message = "<h5> " + addr.location.address + "</h5> <h6> Choose a Geography </h6>";
        $scope.selected_address = addr;
    }
    
    $scope.indicatorInfo = function(event, indicator){
        event.preventDefault();
        $http.get("//" + $scope.app_url + "/profiles/indicator/info/", {params:{
            s:indicator.slug
        }})
        .success(function(data, status, headers, config){
            
            var wW = $(window).width();
            var wH = $(window).height();
            var tW = wW - (wW *.45);
            var tH = wH -(wH *.25);
            $("#info-modal .modal-dialog").css({
                width: tW,
            });
            $("#info-modal .modal-content").css({
                width: tW
            });
            
            $("#info-modal .modal-title").text(indicator.name);
            $("#info-modal .modal-content .modal-body").html(data)
            $('#info-modal').modal('show');
        });
    };

    $scope.mapIt = function(event){
        /*Called when user clicks on Map button*/
        launchDataview(event, $scope);
    }

    $scope.makeSpinner = function () { 
        /*UTIL for creating and managing the loading dio*/
        $scope.activity = true;
    }

    $scope.stopSpinner = function(){
       $scope.activity = false;
    }

    $scope.getIndicatorGeoms = function(){
        /*Dataview 1: Start by Collecting all the geographies for the levels available in this indicator*/

        var proms = []; //collection of http promises
        $scope.geoms = [];

        $scope.level_list = $scope.levels.map(function(obj){
            return obj.name;
        });

        // always grab the reference geography shape
        $http.get($scope.api_url + '/shp/', {params:{geos:$scope.init_record.id}})
        .success(function (data, status, headers, config){
            $scope.reference_layer_data = data;
        });

        $scope.record_sets = {}; // sets of records organized by level that have been evaluated and retrieved
        $scope.times = $scope.indicator.times.sort();
        $scope.time = $scope.times[$scope.times.length -1]; // this gets the last time in the series
        $scope.recordIdstr="";
        
        // collect basic info on records that are in or around this geography
        for(var i in $scope.levels){
            if($scope.levels[i] != $scope.level){
                proms.push($scope.geoQuery($scope.init_record, $scope.level, $scope.levels[i], function(data, targLevel){
                    $scope.record_sets[targLevel.name] = data.objects;
                    $scope.records = $scope.records.concat(data.objects);
                }));
            }
        }
        
        // Collect other geo records at the level of our main geography
        var rLevP = $http.get($scope.api_url + '/geos/level/'+ $scope.level.slug, { params:{ filter:$scope.filter_key }})
        .success(function (data, status, headers, config){
            $scope.record_sets[$scope.level.name] = data.objects;
        });

        proms.push(rLevP);

        $q.all(proms).then(function(results) {
            $scope.enable_tools = true; // this activates our tools.

            /* this sets our Default level that is the level that gets loaded for the user by default Trying first from the hash */
            var hLev = $location.path();
            var lIdx = $scope.getLevelFromSlug(hLev.split("/")[1]);
            if(lIdx != false){
                $scope.level = $scope.levels[lIdx];
            }
            $scope.switchDataLevel($scope.level);
            angular.forEach($scope.records, function(r){
                $scope.recordIdstr += r.id + ",";
            });

        });
    }

    $scope.getGeoIndicatorData = function(level, slug, callback){
        /*Routines that happen everytime you get a load of indicator data
         * This gets one set of data per time for given <level>
         * */
        $scope.makeSpinner();
        var url = $scope.api_url + "/indicator/" + slug + "/";
        var geoms;
        var proms = [];
        var p;

        if(!$scope.data_cache.hasOwnProperty(slug)){
            $scope.data_cache[slug] = {};
        }

        
        //Collect geoms for this level
        geoms = [];
        geoms = $scope.record_sets[level.name].map(function(obj){
              return obj.id;
        });
       
        for(var i in $scope.times){
            var t = $scope.times[i]; // time
        
            // track progress
            if(geoms.length > 0){
                // we need to be able to determine when this time has loaded all of its level data
                p = $http.get(url, { params:{
                                geos:geoms.join(","), 
                                time:t,
                                geom:"t",
                                key:level.name, // this is a hack for adding returning an extra field later. It is the level. It will be made available in config.params
                                },
                                headers: {'Content-Type': 'application/x-www-form-urlencoded'}

                })
                .success(function(data, status, headers, config){
                    //$scope.progress.completed += 1;
                    //$scope.progress.percent = ($scope.progress.completed/$scope.progress.total) * 100;
                }); 
                proms.push(p);
           }
        }
        
        $q.all(proms).then(function(results){
            // add a memo that this level has been loaded.
            $scope.avail_levels[$scope.indicator.slug][level.name] = true;
            for(var i in results){
                // iterating through a level -> time -> dataset
                
                // check to see if the cache has a time member for this indicator
                if(!$scope.data_cache[$scope.indicator.slug].hasOwnProperty(results[i].config.params.time)){ 
                    $scope.data_cache[$scope.indicator.slug][results[i].config.params.time] = {}; // if not add one
                }
                $scope.data_cache[$scope.indicator.slug][results[i].config.params.time][results[i].config.params.key] = results[i].data.objects;  
            }
            if(!angular.isUndefined(callback) && callback != null){
                callback();   
            }
            $scope.stopSpinner();
            
        });
    }

    $scope.generateTables = function(){
        /*Parse out data cache and generate tables. Happens Once */
        var table_data = {}; // contains data organized by Level names
        var n;
        for(var t in $scope.data_cache[$scope.indicator.slug]){
            /* HERE we are iterating times in  data_cache: Ex: {2000: Object, 2010: Object} */
            for(var lev in $scope.data_cache[$scope.indicator.slug][t]){
                /* iterate levels within the time */
                if(!table_data.hasOwnProperty(lev)){
                    /*Create a level item if it doesnt exist*/
                    table_data[lev] = [];
                }
                for(var rec in $scope.data_cache[$scope.indicator.slug][t][lev]){
                    n = $scope.data_cache[$scope.indicator.slug][t][lev][rec].properties.label;
                    if(!table_data[lev].hasOwnProperty(n)){
                        table_data[lev][n] = {};
                    }

                    table_data[lev][n][t] = {
                        value:$scope.data_cache[$scope.indicator.slug][t][lev][rec].values[$scope.indicator.key],
                        moe: $scope.moe($scope.data_cache[$scope.indicator.slug][t][lev][rec].values.moe),
                        value_type : $scope.data_cache[$scope.indicator.slug][t][lev][rec].values.value_type,
                        numerator: $scope.data_cache[$scope.indicator.slug][t][lev][rec].values.numerator || null,
                        numerator_moe: $scope.moe($scope.data_cache[$scope.indicator.slug][t][lev][rec].values.numerator_moe), 
                        number: $scope.data_cache[$scope.indicator.slug][t][lev][rec].values.number || null

                    };
                }
            }
        }
        
        // finally clean up the data into a more sensible array
        var a; // resuable array
        var d; // reusable obj
        for(var k in table_data){
            a = [];
            for(var l in table_data[k]){
                d = {};
                d = angular.extend(d, table_data[k][l]);
                d['label'] = l;
                a.push(d);
            }

            table_data[k] = a;
        }
        $scope.table_data = table_data;
        $timeout(function(){
            $(".moe").tooltip();
        }, 200)
        $scope.updateTable();

    } 

    $scope.updateMapData = function(){
        /*Updates Displayed map data*/
        var mouseEvents = {
            mouseover:function(e){
                  var valueKey = $scope.indicator.key;
                  var l = e.target;
                  var props = l.feature.geometry.properties;
                  var vals = l.feature.geometry.values;
                  var info_text = '<h4>'+props.label+'</h4>';
                  var value_text ="";
                  if($scope.disp_opts.value_format.hasOwnProperty("rules")){
                    for(var i = 0; i < $scope.disp_opts.value_format.rules.length; i++){
                        if(vals["f_"+valueKey] == $scope.disp_opts.value_format.rules[i].value_operator){
                            value_text = "<h5>" + $scope.disp_opts.value_format.rules[i].display_value;
                            break;
                        }
                        else{
                            value_text = "<h5>" + $scope.value_formatter(vals[valueKey]||-999999);
                        }
                    }
                    info_text += value_text;
                  }else{
                    try{
                        custom = custom_value(vals[valueKey]);
                        if (custom==vals[valueKey]){
                           info_text += "<h5>" + $scope.value_formatter(vals[valueKey]||-999999);
                        }
                        else{
                           info_text += "<h5>" + custom;}
                    }
                    catch(err){
                        info_text += "<h5>" + $scope.value_formatter(vals[valueKey]||-999999);
                    }
                  }
                  if(vals.moe){
                    info_text+= " +/- " + vals["f_moe"];
                  }
                  info_text += "</h5>";
                  $scope.pm.infoBox.update(info_text);
                  $scope.pm.highlightLayer(e);
                  // highlight the table cell
                  var td = $("#" + props.label.replace(/\s/g, "\\ ").replace(/\./g, "\\.").replace(/\'/g, "\\\'"));
                  td.addClass("td-highlight");
                  var dt = $(".data-table");
                  dt.scrollTop(0);
                  dt.scrollTop(td.offset().top-(td.height()*4));

            },
            mouseout:function(e){
                var layer = e.target;
                var props = layer.feature.geometry.properties;
                $scope.pm.unhighlightLayer(e);
                $scope.pm.infoBox.update();
                $("#" + props.label.replace(/\s/g, "\\ ").replace(/\./g, "\\.").replace(/\'/g, "\\\'")).removeClass("td-highlight");
                var dt = $(".data-table");
                dt.scrollTop(0);
            },
            click:function(){

            }  
        }
        var data = {'objects':$scope.data_cache[$scope.indicator.slug][$scope.time][$scope.level.name]};
       
        var base_layer = $scope.pm.DataPolyFeatureGroup($scope.reference_layer_data, {
            weight:2,
            opacity:1,
			fill:false,
			color:"#444",
			dashArray: '5',
        
        });

        var choro = $scope.pm.DataChoroplethFeatureGroup(data,
                $scope.indicator.key, mouseEvents, 
                $scope.disp_opts['legend'],
                $scope.disp_opts['value_format'],
                "<h3>%s</h3><div class='clear'></div>".replace("%s", $scope.time)
                );
        if(!angular.isUndefined($scope.active_layers)){
            $scope.pm.map.removeLayer($scope.active_layers.base);

            try{
                $scope.pm.map.removeLayer($scope.active_layers.layer);
                $scope.pm.map.removeControl($scope.active_layers.control);
            }catch(e){
                //..
            }
        }

        $scope.active_layers = {'layer':choro[0], 'control':choro[1], 'base':base_layer};
        if(choro !== false){
            // couldnt generate a map for this time, we'll disable it.
            choro[0].addTo($scope.pm.map);
            choro[1].addTo($scope.pm.map);
            base_layer.addTo($scope.pm.map);
            $scope.pm.map.fitBounds(choro[0].getBounds());

        }else{
            base_layer.addTo($scope.pm.map);
            base_layer.setStyle({
                'fill':true,
                'fillColor':"gray"
            });
            $scope.pm.map.fitBounds(base_layer.getBounds());
        }


    }

    $scope.switchTime = function(time){
        $scope.time = time;
        $scope.updateMapData();
    }

    $scope.geoLabelSort = function(item){
        var k;
        if(item.hasOwnProperty("label")){
            k = item.label;

        }else{
            k = item.name;
        }

        if(k.toString().search(/\d+/) !== -1){
            return parseFloat(k.toString().replace(/[a-zA-Z\!\s]+/g, ''));
        }else{
            return k;
        }
    }

    $scope.updateTable = function(){
        
        var escapedName = $scope.level.name.replace(/\s/g, "\\ ");
        $timeout(function(){
            $scope.tableReverse = true; // set back to default
            $scope.sortTable('label'); // always resort by label
            tableize("#table-data-"+escapedName); 
        }, 20);
    }

    $scope.switchDataLevel = function(level){

        if($scope.avail_levels[$scope.indicator.slug].hasOwnProperty(level.name)){
            $scope.level = level;
            if($scope.indicatorOptions != false){
                $scope.generateTables();                
            }
            $scope.updateMapData();
            $scope.updateTable();
        }else{
            $scope.getGeoIndicatorData(level, $scope.indicator.slug, function() {
                $scope.level = level;
                $scope.updateMapData();
                $scope.generateTables();
            });
        }
    }

    $scope.changeIndicator = function(i){
        $scope.switchDataLevel($scope.level)
    }
    
    $scope.sortTable = function (sortKey){
        var aC, bc = null;
        $scope.tableReverse = !$scope.tableReverse; 
        if($scope.tableReverse){
            $scope.sortClass  = 'glyphicon-chevron-up';
        }else{
            $scope.sortClass  = 'glyphicon-chevron-down';
            
        }
        $scope.table_data[$scope.level.name].sort(function(a, b){
            if(a[sortKey] == null || b[sortKey] == null ){
                return -1;
            }
            
            if(a[sortKey].toString().search(/\d+/) !== -1){
                aC = parseFloat(a[sortKey].toString().replace(/[a-zA-Z\!\s]+/g, ''));
                bC = parseFloat(b[sortKey].toString().replace(/[a-zA-Z\!\s]+/g, ''));
                if ($scope.tableReverse == false){
                    if(aC < bC) return 1;
                    if(aC > bC) return -1;
                }else{
                    if(aC > bC) return 1;
                    if(aC < bC) return -1;
                }
            }else{
                aC = a[sortKey];
                bC = b[sortKey];
                if ($scope.tableReverse == false){
                    if(aC < bC) return -1;
                    if(aC > bC) return 1;
                }else{
                    if(aC > bC) return -1;
                    if(aC < bC) return 1;
                }
            }
        });

    }

    $scope.objKeys = function(obj){
        /*Return the list of keys from obj*/
        var keys=[];
        angular.forEach(obj, function(v, k){
            keys.push(k);
        });
        return keys;
    }

    $scope.arrayDiff = function(arr1, arr2){
        /* You'll want to use larger item as arr1*/
        var diff = [];
        angular.forEach(arr1, function(key) {
            if (arr2.indexOf(key) == -1) {
                diff.push(key);
            }
        });
        return diff;
    }

    $scope.launchPrintFriendly = function(){
        // launch a print friendly version of the dataview page we are in
        window.open($window.location.href);
    }
    
    $scope.init = function(){
        $scope.levels = window.LEVELS; // set levels
        $scope.level = $scope.levels[$scope.getLevelFromSlug(window.LEVEL.slug)]; // the currently selected level
        $scope.init_level = $scope.level; // store intial level for for later
        $scope.init_record = window.RECORD;
        $scope.filter_key = window.FILTER_KEY;
        $scope.census_id = window.CENSUS_ID;
        $scope.domain = window.DOMAIN;
        $scope.indicator = window.INDICATOR || undefined;
        $scope.indicatorOptions = window.INDICATOR_OPTIONS || false;
        if($scope.indicatorOptions!=false){$scope.indicator = $scope.indicatorOptions[0]};
        $scope.app_url = window.APP_URL;
        $scope.api_url = window.API_URL;
        $scope.tableReverse = true;
        $scope.pm = new ProfilesMap();
        if(!angular.isUndefined(window.DISP_OPTS)){$scope.value_formatter = $scope.pm.getFormatter(window.DISP_OPTS.value_format)};

        // doc ready after init
        $(function(){
            $scope.pm.defaultView= window.CENTER_MAP; // ex:[41.83, -71.41];
            $scope.pm.init();
            $scope.pm.infoBox = $scope.pm.makeInfoBox('info label', "<h4>"+ $scope.init_record.name +"</h4>");
            $scope.pm.infoBox.addTo($scope.pm.map);
            
            // get intial data
            if(angular.isUndefined($scope.indicator)){
                $scope.records = [window.RECORD];
                var l = $scope.$storage.levelstate;
                var lStateExpire = 10 // minutes
                if(l != null){
                    // check to see if this level change history hasnt expired
                    if((Date.now() - l.time) < (lStateExpire * 60000)){
                        //update scope level
                        //can not load to state level
                        /*if($scope.init_level.slug != l.level.slug){
                            $scope.updateLev(l.level);
                        }else{*/
                            // behave normally
                            $scope.getGeoms();
                            $scope.getRecordsByLev($scope.level.slug, true);
                        //}
                    }else{
                        // expired level history
                        // behave normally
                        $scope.getGeoms();
                        $scope.getRecordsByLev($scope.level.slug, true);
                        // clear out the history token
                        $scope.$storage.levelstate = null;
                    }

                }else{
                    $scope.getGeoms();
                    $scope.getRecordsByLev($scope.level.slug, true);
                }
                // domain_view
                var p = $location.path().split("/"); // ex: ["", "demographics-overview", "Other"]
                if(p.length == 3){
                    // parse the hash and open groups
                    var targ = $("#" + p[1] + " #" + p[2].replace(/\s/g, "\\ ").replace(/,/g, "\\,")); // TODO: DRY this up.
                    targ.click(); // TODO:silly hack.

                    // We need to scroll 
                    $('body').animate({ scrollTop: targ.offset().top});
                }
               
            }else{
                $scope.disp_opts = window.DISP_OPTS;
                $scope.records = [window.RECORD]; // active records as in active geography records that we are looking at
                $scope.getIndicatorGeoms();
                $scope.avail_levels = {}; // create an available levels index. that is levels thave loaded data for a given indicator
                
                $scope.wTop = window.top === window.self;

                if($scope.indicatorOptions != false){
                    for(var i in $scope.indicatorOptions){
                        $scope.avail_levels[$scope.indicatorOptions[i].slug] = {};
                    }
                    $scope.init_indicator = $scope.indicator;
                }else{
                    $scope.init_indicator = $scope.indicator;
                    $scope.avail_levels[$scope.indicator.slug] = {};
                }

            }
                         
        });
        try{
            window.INIT();
        }catch(e){

        }
    }

    $scope.init();
}


function SearchCtrl($scope, launchDataview){
    $scope.mapIt = function(event, indicator){
        $scope.indicator = JSON.parse(indicator);
        launchDataview(event, $scope);
    }
}


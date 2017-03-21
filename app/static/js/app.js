var myApp = angular.module('KnoWhere', ["ui.bootstrap"]);

myApp.controller('MainController', function MainController() {
  this.name = "KnoWhere";
});

/*** Define factories ***/


function addZ(n){return n<10 ? '0' + n : ''+n;}
function dateToStr(d, fmt){
  if(fmt == "ymd"){
    return d.getFullYear() + "-" + addZ(d.getMonth()+1) + "-"  + addZ(d.getDate());
  } else {
    return d.toDateString();
  }
}

/*** FORM ***/
myApp.service("shared", function($http){
  var users = []
  var usernames = []
  var the_username = undefined
  var the_user_id = undefined
  var user_data = undefined
  var user_data_first = undefined
  var first_date = undefined
  var user_data_last = undefined
  var last_date = undefined
  var map_latlong = undefined
  var d = new Date()
  var start_date = d
  var end_date = d
  var overviewdate=document.getElementById("overview-date")
  var mapdate=document.getElementById("map-date")
  var total_distance = "N/A"

  var get_first_data = function(){
    if(user_data !== []){
      return user_data.filter(function(entry){
        return ("latitude" in entry) && (
          dateToStr(start_date,"ymd")==entry.date.substring(0,10) || 
              user_data[0].date.substring(0,10)==entry.date.substring(0,10)
        )
      });
    } else {
      return []
    }
  };

  var get_last_data = function(){
    if(user_data !== []){
      return user_data.filter(function(entry){
        return ("latitude" in entry) && (
          dateToStr(end_date,"ymd")==entry.date.substring(0,10) || 
              user_data[user_data.length-2].date.substring(0,10)==entry.date.substring(0,10)
        )
      });
    } else {
      return []
    }
  };

  var get_total_distance = function(){
    if(user_data !== []){
      return user_data.filter(function(entry){
        return "total_distance" in entry;
      });
    } else {
      return []
    }
  };

  var get_map_latlong = function(){
    if(user_data_last !== []){
      return user_data_last.map(function(entry){return [entry.latitude,entry.longitude]});
    } else{
      return [];
    }
  }

  return {
    queryUsers: function() {
      return $http({
        method: "GET",
        url: "/query_users"
      }).then(function(response){
        users = response.data
        usernames = users.map(function(x){return x.username})
      });
    },
    getTotalDistance: function() {return total_distance},
    getUser: function(){return the_username;},
    getUsers: function(){return users.map(function(u){return u.username})},
    getStartDate: function() {return start_date;},
    getEndDate: function(){return end_date;},
    setUser: function(uname){
      if(usernames.indexOf(uname) > -1){
        the_username = uname;
        //the_user_id = users.filter(function(x){return x["username"]==uname})[0]._id;
      }
    },
    setStartDate: function(d){
      start_date = d;
      //console.log(d);
    },
    setEndDate: function(d){
      end_date = d;
      //console.log(d);
    },
    getData: function(){
      var s_date = start_date.getFullYear() + "-" + 
                  (start_date.getMonth()+1) + "-" + 
                  start_date.getDate() + 
                  " 00:00:00.000";
      var e_date_plus_1 = new Date(end_date);
      e_date_plus_1.setDate(e_date_plus_1.getDate() + 1)
      var e_date = e_date_plus_1.getFullYear() + "-" +
                  (e_date_plus_1.getMonth()+1) + "-" +
                  e_date_plus_1.getDate() +
                  " 00:00:00.000";

      return $http({
        method: "GET",
        url: "/query_iphone_test_GPS",
        params: {
          user_name: the_username,
          min_date: s_date,
          max_date: e_date
        }
      }).then(function(response){
        user_data = response.data;
        //console.log(user_data)
        user_data_first = get_first_data();
        user_data_last = get_last_data();
        first_date = new Date(user_data_first[0].date)
        last_date = new Date(user_data_last[0].date)
        //console.log(first_date)
        //console.log(last_date)
        map_latlong = get_map_latlong();
        overviewdate.innerText = dateToStr(first_date, "") + " \u2013 " + dateToStr(last_date, "");
        mapdate.innerText = dateToStr(last_date, "");
        total_distance = (get_total_distance()[0]["total_distance"]).toFixed(2);
        //console.log(total_distance)
        draw(map_latlong);
      });
    }
  }
});

myApp.controller("FormController", function($scope, shared, Users){
  shared.queryUsers()
  //this.selected_user = shared.getUser();
  d = new Date();
  this.today = dateToStr(d, "ymd")
  this.setStartDate = shared.setStartDate;
  this.setEndDate = shared.setEndDate;
  this.setUser = shared.setUser;
  this.getUsers = shared.getUsers

  this.start_date = shared.getStartDate();
  this.end_date = shared.getEndDate();
  this.getData = shared.getData
  //this.setStartDate(this.start_date)
  //this.setEndDate(this.end_date)
});

myApp.factory("Users", function($http){
  return {
    getUserData: function(fname) {
      return $http.get("/getData")
    }
  };
  //return ["Andrew", "Bill", "Emil", "Glen"];
});


myApp.factory("Dates", function(){
  return 0 //get min and max dates from the returned data;
});


/*** OVERVIEW ***/
myApp.controller("OverviewController", function($scope, shared){

  start_date = shared.getStartDate()
  end_date = shared.getEndDate()
  this.date_range = toDateRange(start_date, end_date);
  this.getTotalDistance = shared.getTotalDistance;
  
  $scope.$watch(function(){
    return shared.getStartDate();
  }, function (newVal, oldVal, scope){
    if(newVal !== undefined){
      start_date = newVal;
    }
    scope.overview.date_range = toDateRange(start_date, end_date);
  });

  $scope.$watch(function(){
    return shared.getEndDate();
  }, function (newVal, oldVal, scope){
    if(newVal !== undefined){
      end_date = newVal;
    }
    scope.overview.date_range = toDateRange(start_date, end_date)
  });

  function toDateRange(start_date, end_date){
    if(start_date == end_date){
      date_range = dateToStr(end_date, "");
    } else {
      date_range = dateToStr(start_date, "") + " \u2013 " + dateToStr(end_date, "");
    }

    return date_range
  }

});


/*** MAP ***/
myApp.controller("MapController", function($scope, shared){

  end_date = shared.getEndDate()
  this.date = dateToStr(end_date, "");
  
  $scope.$watch(function(){
    return shared.getEndDate();
  }, function (newVal, oldVal, scope){
    if(newVal !== undefined){
      end_date = newVal;
    }
    scope.map.date = dateToStr(end_date, "");
  });

});
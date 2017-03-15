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
  var users = [];
  var usernames = []
  var the_user = undefined;
  var the_user_id = undefined
  var user_data = undefined;
  var d = new Date();
  var start_date = d;
  var end_date = d;

  var queryUser = function(uid){
      return $http({
        method: "GET",
        url: "/query_iphone_test",
        params: {user_id: uid}
      }).then(function(response){
        user_data = response.data
        //console.log(user_data);
      });
    };

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
    getUser: function(){return the_user;},
    getUsers: function(){return users.map(function(u){return u.username})},
    getStartDate: function() {return start_date;},
    getEndDate: function(){return end_date;},
    setUser: function(uname){
      if(usernames.indexOf(uname) > -1){
        the_user = uname;
        the_user_id = users.filter(function(x){return x["username"]==uname})[0]._id;
        queryUser(the_user_id);
      }
    },
    setStartDate: function(d){start_date = d;},
    setEndDate: function(d){end_date = d;}
  }
});

myApp.controller("FormController", function($scope, shared, Users){
  shared.queryUsers()
  //this.selected_user = shared.getUser();
  d = new Date();
  this.today = dateToStr(d, "ymd")
  this.start_date = shared.getStartDate();
  this.end_date = shared.getEndDate();
  this.setStartDate = shared.setStartDate;
  this.setEndDate = shared.setEndDate;
  this.setUser = shared.setUser;
  this.getUsers = shared.getUsers


  //console.log(Users.getUniqueUsers())
  /*Users.getUniqueUsers().then(function(response){
    console.log(response.data[0]["names"])
      this.users = response.data[0]["names"]
  });*/
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
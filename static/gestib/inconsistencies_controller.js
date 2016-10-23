

app.controller("inconsistenciesController", function($scope, $http) {

    $http.get('/gestib/getDuplicates').then(function(response) {
        console.log(response);
        $scope.dups = response.data;
    });

});

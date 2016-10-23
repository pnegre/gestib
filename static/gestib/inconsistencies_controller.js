

app.controller("inconsistenciesController", function($scope, $http) {

    $http.get('/gestib/getDuplicates').then(function(response) {
        $scope.dups = response.data;
    });

});

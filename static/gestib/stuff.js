
var app = angular.module('app', []);
// Canviem configuració per símbols per interpolar variables
// Si no, tenim conflictes amb les templates de django
// perquè també empren "{{" i "}}"
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('//');
    $interpolateProvider.endSymbol('//');
});

// Això és per enviar el csrftoken a partir de la cookie o header
// amb cada petició ajax que fem amb angularjs
app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

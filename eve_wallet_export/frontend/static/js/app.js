'use strict';

var app = angular.module('eveWalletExportApp', [] );

app.directive('apiForm', function(){
    return {
        restrict: 'E',
        templateUrl: 'resources/api-form.html',
        controllerAs: 'apiCtrl'
    };
});

app.directive('walletSelector', ['$http', function($http){
    return {
        restrict: 'E',
        templateUrl: 'resources/wallet-selector.html',
        controller: function (){
            var ctrl = this
            ctrl.wallets = []
            ctrl.errorMessage = ''
            ctrl.checkKey = function(key, code){
                ctrl.wallets = []
                ctrl.errorMessage = ''
                var success = function(response){
                    ctrl.wallets = response.data.wallets
                }
                var failure = function(response){
                    ctrl.errorMessage = response.data.message
                }
                $http.get('/api/wallet/', {params: {key: key, code: code}}).then(success, failure)
            };
        },
        controllerAs: 'walletsCtrl'
    };
}]);


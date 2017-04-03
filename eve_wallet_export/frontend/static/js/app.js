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
            ctrl.types = ''
            ctrl.errorMessage = ''
            ctrl.checkKey = function(key, code){
                ctrl.wallets = []
                ctrl.errorMessage = ''
                var success = function(response){
                    ctrl.types = response.data.types;
                    var walletResponse = response.data.wallets;
                    ctrl.wallets = ctrl.iterWallets(walletResponse)
                }
                var failure = function(response){
                    ctrl.errorMessage = response.data.message
                }
                $http.get('/api/wallet/', {params: {key: key, code: code}}).then(success, failure)
            };
            ctrl.iterWallets = function(wallets){
                if (ctrl.types == "Corporation"){
                    var wallet = wallets[0]
                    var divisions = []
                    for (var index in wallet.divisions){
                        division=wallet.divisions[index]
                        console.log(division)
                        division.portrait = 'https://image.eveonline.com/Corporation/' + wallet.corporationID + '_64.png'
                        divisions.push(division)
                    }
                    return divisions
                }
                else if (ctrl.types == "Character"){
                    var divisions = []
                    var division
                    for (wallet in wallets){
                        wallet.divisions[0].portrait = 'https://image.eveonline.com/Character/' + wallet.characterID + '_64.png'
                        divisions.push(wallet.division[0])
                    }
                    return divisions
                }
            }
        },
        controllerAs: 'walletsCtrl'
    };
}]);


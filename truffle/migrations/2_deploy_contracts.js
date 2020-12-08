var RocketToken = artifacts.require("./RocketToken.sol");
var RocketTokenSale = artifacts.require("./RocketTokenSale.sol");
module.exports = function (deployer) {
  deployer.deploy(RocketToken, 1000000).then(function(){
  
  var tokenPrice = 1000000000000000; // in wei
  return deployer.deploy(RocketTokenSale, RocketToken.address, tokenPrice);
  });
};
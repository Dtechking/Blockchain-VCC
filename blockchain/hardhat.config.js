require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.28",
};

module.exports = {
  defaultNetwork: "ganache",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",
      accounts: [
        '0x46fc940c2707686647dbe54a1d21ec7e04df7be8d9b858e7a8d81f801263daa9', // Use private key from Ganache (without 0x, paste multiple if needed)
        '0x478a4e49b27773d5e1e0d8463f2365cc6adf2528c3315646a02b2ccc9b9221a8'
      ]
    }
  },
  solidity: "0.8.28"
};

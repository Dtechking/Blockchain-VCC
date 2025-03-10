// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TrafficDataStorage {
    mapping(string => string) private dataRecords;

    function addData(string memory vehicleID, string memory encryptedData) public {
        dataRecords[vehicleID] = encryptedData;
    }

    function getData(string memory vehicleID) public view returns (string memory) {
        return dataRecords[vehicleID];
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract TrafficEventLogger {

    // Struct to store detailed event data
    struct TrafficEvent {
        string eventId;
        uint256 timestamp;
        string eventType;
        bytes32 eventHash;
        string vehicleAddress;
        string location;
        string eventDetails;
        bytes signature;
        address rsuAddress;
    }

    // Mapping to store event logs, event ID (string) => TrafficEvent
    mapping(string => TrafficEvent) public events;

    // Event to be emitted when a new event is logged
    event EventLogged(
        string eventId,
        string eventType,
        bytes32 eventHash,
        string vehicleAddress,
        string location,
        string eventDetails,
        address rsuAddress,
        uint256 timestamp
    );

    // Function to log a new event
    function logAlert(
        string memory _eventId,
        string memory _eventType,
        bytes32 _eventHash,
        string memory _vehicleAddress,
        string memory _location,
        string memory _eventDetails,
        bytes memory _signature
    ) public returns (string memory) {

        events[_eventId] = TrafficEvent({
            eventId: _eventId,
            timestamp: block.timestamp,
            eventType: _eventType,
            eventHash: _eventHash,
            vehicleAddress: _vehicleAddress,
            location: _location,
            eventDetails: _eventDetails,
            signature: _signature,
            rsuAddress: msg.sender
        });

        emit EventLogged(
            _eventId,
            _eventType,
            _eventHash,
            _vehicleAddress,
            _location,
            _eventDetails,
            msg.sender,
            block.timestamp
        );

        return _eventId;
    }

    // Function to get event details by event ID (string)
    function getEventDetails(string memory eventId) public view returns (TrafficEvent memory) {
        return events[eventId];
    }
}

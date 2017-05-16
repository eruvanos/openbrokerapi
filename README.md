# CF Broker Lib

A Python package for building V2 Cloud Foundry Service Brokers.


## Installation

This package will be available via pip3 in a while. Until that use

´´´
pip3 install git+https://github.com/eruvanos/cfbrokerapi.git
´´´

## Usage

TODO

## Error Types
brokerapi defines a handful of error types in service_broker.py
for some common error cases that your service broker may encounter.
Raise these from your ServiceBroker methods where appropriate,
and brokerapi will do the "right thing" (™), 
and give Cloud Foundry an appropriate status code, 
as per the Service Broker API specification.

## Roadmap

* [x] implement: catalog
* [x] implement: provisioning
* [ ] implement: deprovisioning
* [ ] implement: bind
* [ ] implement: unbind
* [ ] implement: update
* [ ] integration test
* [ ] secure endpoints with  basic auth
* [ ] support async
* [ ] Add "Getting started" to Readme
* [ ] refactor modules
* [ ] available via pip3 (without git url)

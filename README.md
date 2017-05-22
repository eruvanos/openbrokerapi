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
* [x] implement: deprovisioning
* [x] start testing
* [x] implement: bind
* [x] implement: unbind
* [x] implement: update
* [x] secure endpoints with basic auth
* [ ] Add "Getting started" to Readme
* [ ] support async
* [ ] refactor modules
* [ ] support VolumeMounts
* [ ] Create example broker
* [ ] available via pip3 (without git url)
  * [x] setup setup.py
  * [x] register on pypi test
  * [ ] register on pypi

## Not Supported

* Provisioning
  * Response: 200 - If service already exists, a 409-Conflict will be returned
* Bind
  * Response: 200 - If binding already exists, a 409-Conflict will be returned 

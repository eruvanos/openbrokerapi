# Service Broker API

A Python package for building Service Brokers.

Following [CF Service Broker API](https://docs.cloudfoundry.org/services/api.html)
and
[Open Service Broker API](https://www.openservicebrokerapi.org/)

## Installation

This package is available for Python 3.5+.

```bash
pip3 install openbrokerapi
```

Or install the development version from github:

```bash
pip3 install git+https://github.com/eruvanos/openbrokerapi.git
```

## Getting started

```python
from flask import Flask
from openbrokerapi import service_broker
from openbrokerapi.api import *
from openbrokerapi.log_util import *

# Implement a service broker by overriding methods of ServiceBroker
class CustomServiceBroker(service_broker.ServiceBroker):
    def catalog(self) -> List[Service]:
        pass

    def provision(self, instance_id: str, service_details: ProvisionDetails, async_allowed: bool) -> ProvisionedServiceSpec:
        pass

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        pass

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        pass

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        pass

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
        pass
    
    def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
        pass

# Simpely start the server
serve(CustomServiceBroker(), BrokerCredentials("", ""))

# or register blueprint to your own FlaskApp instance
app = Flask(__name__)
logger = basic_config() #  Use root logger with a basic configuration provided by openbrokerapi.log_utils
openbroker_bp = get_blueprint(CustomServiceBroker(), BrokerCredentials("",""), logger)
app.register_blueprint(openbroker_bp)
app.run("0.0.0.0")
```

## Error Types
Brokerapi defines a handful of error types in errors.py
for some common error cases that your service broker may encounter.
Raise these from your ServiceBroker methods where appropriate,
and brokerapi will do the "right thing" (™), 
and give Cloud Foundry an appropriate status code, 
as per the Service Broker API specification.

## Planned

* Support async tasks
* Support VolumeMounts

## Not Planned To Support

* Provisioning
    * Response: 200 - If service already exists, a 409-Conflict will be returned
* Bind
    * Response: 200 - If binding already exists, a 409-Conflict will be returned 

## Bugs or Issues

Please report bugs, issues or feature requests to [Github Issues](https://github.com/eruvanos/openbrokerapi/issues)


## Release Notes

###### v0.3dev

###### v0.2
* improve testing
* fix: Bind and update getting dict instead of expected objects
* support async for provision, update, deprovision
* Handle unexpected exception with global error_handler (responding with 500)
* get_blueprint() now expects a logger
* add log_utils with basic_config()

###### v0.1
* initial version
* supported operations
  * provision
  * update
  * bind
  * unbind
  * deprovision
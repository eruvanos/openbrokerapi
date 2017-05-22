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

## Getting started

```python
from openbrokerapi import service_broker
from openbrokerapi.api import *
from flask import Flask

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

# Simpely start the server
serve(CustomServiceBroker(), BrokerCredentials("", ""))

# or register blueprint to your own FlaskApp instance
app = Flask(__name__)
openbroker_bp = get_blueprint(CustomServiceBroker(), BrokerCredentials("",""))
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
# CF Broker Lib

A Python package for building V2 Cloud Foundry Service Brokers.

[Following CF Broker API](https://docs.cloudfoundry.org/services/api.html)

## Installation

This package is available for Python 3.5+.

```bash
pip3 install cfbrokerapi
```

## Getting started

```python
# Implement a service broker by overriding methods of ServiceBroker
class CustomServiceBroker(ServiceBroker):
    def catalog(self) -> List[Service]:
        pass

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        pass

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        pass

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -SimplyeServiceSpec:
        pass

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        pass

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
        pass    

# Simpely start the server
cfbrokerapi.serve(CustomServiceBroker(), BrokerCredentials("basicUser", "Password"), port=5000)
```

## Error Types
brokerapi defines a handful of error types in errors.py
for some common error cases that your service broker may encounter.
Raise these from your ServiceBroker methods where appropriate,
and brokerapi will do the "right thing" (™), 
and give Cloud Foundry an appropriate status code, 
as per the Service Broker API specification.

## Not Supported

* Provisioning
    * Response: 200 - If service already exists, a 409-Conflict will be returned
* Bind
    * Response: 200 - If binding already exists, a 409-Conflict will be returned 

## Bugs or Issues

Please report bugs, issues or feature requests to [Github Issues](https://github.com/eruvanos/cfbrokerapi/issues)
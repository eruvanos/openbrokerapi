Architecture
============

Service: Open Servicebroker API Object, representing a service
ServiceProvider: Profides ONE service
ServiceBroker: Provide functionality to interact with multiple Services
ServiceBrokerRouter: Provides an additional layer of indirection, to manage services from different broker implementations

Scenarios
---------

Single Broker - One/Multiple Service
+++++++++++++++++++++++++++

Most basic setup, but supports the full set of features of OpenServiceBroker API.


.. include:: ./_static/single_broker.py
    :code: python


Seperate Brokers - Seperate broker implementations
++++++++++++++++++++++++++++++++++++

Most dynamic setup, a `Router` object forwards requests to seperate broker implementations


.. include:: ./_static/seperated_broker.py
    :code: python


Implement a ServiceProvider
---------------------------

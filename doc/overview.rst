Overview
========

Service: Open Servicebroker API Object, representing a service
ServiceBroker: Provide functionality to interact with one or multiple Services
Router: Provides an additional layer of indirection, to manage services from different broker implementations

Scenarios
---------

Provide one or more services with one broker
++++++++++++++++++++++++++++++++++++++++++++

Most basic setup, but supports the full set of features of OpenServiceBroker API.


.. include:: ./_static/single_broker.py
    :code: python


Separate implementations as independent brokers
+++++++++++++++++++++++++++++++++++++++++++++++

Most dynamic setup, a `Router` object forwards requests to seperate broker implementations.


.. include:: ./_static/seperated_broker.py
    :code: python

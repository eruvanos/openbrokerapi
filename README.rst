|Build Status| |Coverage Status| |Known Vulnerabilities| |PYUP|

Open Broker API
===============

A Python package for building Service Brokers supporting API version 2.13+.

Following `Open Service Broker
API Spec <https://github.com/openservicebrokerapi/servicebroker/blob/master/spec.md>`__ and `Open
Service Broker API <https://www.openservicebrokerapi.org/>`__

Check out the documentation_.

.. _documentation: http://openbrokerapi.readthedocs.io/en/latest/

To find out more about Platform Compatibility for OSBAPI versions, check out
`Platform Compatibility for OSBAPI <https://github.com/openservicebrokerapi/servicebroker/blob/master/compatibility.md>`__

 Not all features are supported with this library due to conflicting features.

Installation
------------

This package is available for Python 3.5+.

.. code:: bash

    pip3 install openbrokerapi

    # including gevent as server
    pip3 install openbrokerapi[gevent]

Or install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/eruvanos/openbrokerapi.git

Usage
-----

You can start with a `skeleton project <https://github.com/eruvanos/openbrokerapi-skeleton>`__ or just from scratch.

.. code:: python

   from flask import Flask
   from openbrokerapi import api
   from openbrokerapi.catalog import (
       ServicePlan,
   )
   from openbrokerapi.log_util import basic_config
   from openbrokerapi.service_broker import (
       ServiceBroker,
       Service,
       ProvisionedServiceSpec,
       UpdateServiceSpec,
       Binding,
       DeprovisionServiceSpec,
       LastOperation,
       UnbindDetails,
       ProvisionDetails,
       UpdateDetails,
       BindDetails,
       DeprovisionDetails
   )


   class ExampleServiceBroker(ServiceBroker):
       def catalog(self):
           return Service(
               id='00000000-0000-0000-0000-000000000000',
               name='example-service',
               description='Example Service does nothing',
               bindable=True,
               plans=[
                   ServicePlan(
                       id='00000000-0000-0000-0000-000000000000',
                       name='small',
                       description='example service plan',
                   ),
               ],
               tags=['example', 'service'],
               plan_updateable=True,
           )

       def provision(self, instance_id: str, service_details: ProvisionDetails,
                     async_allowed: bool) -> ProvisionedServiceSpec:
           pass

       def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
           pass

       def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
           pass

       def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
           pass

       def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
           pass

       def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
           pass


   # Simply start the server
   api.serve(ExampleServiceBroker(), api.BrokerCredentials("", ""))

   # or start the server without authentication
   api.serve(ExampleServiceBroker(), None)

   # or start the server with multiple authentication
   api.serve(ExampleServiceBroker(), [api.BrokerCredentials("", ""), api.BrokerCredentials("", "")])

   # or with multiple service brokers and multiple credentials
   api.serve_multiple([ExampleServiceBroker(), ExampleServiceBroker()], [api.BrokerCredentials("", ""), api.BrokerCredentials("", "")])

   # or register blueprint to your own FlaskApp instance
   app = Flask(__name__)
   logger = basic_config()  # Use root logger with a basic configuration provided by openbrokerapi.log_utils
   openbroker_bp = api.get_blueprint(ExampleServiceBroker(), api.BrokerCredentials("", ""), logger)
   app.register_blueprint(openbroker_bp)
   app.run("0.0.0.0")

Deployment
----------
The included :code:`api.serve` function provides a server setup for **local usage only**.

For productive deployments use the blueprint from :code:`api.get_blueprint` to
setup a production ready server like `Waitress <https://docs.pylonsproject.org/projects/waitress/en/latest/>`__
or other mentioned in `Flask Deployment Docs <http://flask.pocoo.org/docs/dev/deploying/wsgi-standalone/>`__

Error Types
-----------

Openbrokerapi defines a handful of error types in errors.py for some
common error cases that your service broker may encounter. Raise these
from your ServiceBroker methods where appropriate, and openbrokerapi
will do the "right thing" (™), and give Cloud Foundry an appropriate
status code, as per the Service Broker API specification.

Internal Notes
--------------

- Context object from update 2.12 and 2.13 is made available, but partially checked (only organization_guid and space_guid). This can change, when an update removes the redundant fields.

Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues`_


How to contribute
-----------------

You want to contribute, I really appreciate!

So let us check how you can contribute:

- Create an issue in the `Github Issues`_. Please provide all information that you think are usefull to solve it.
- Use the `Github Issues`_ to create a feature request, so we can discuss and find a good interface for that feature.
- Create a Pull Request. There are some things that will make it easier to review your Pull Request:
    - Use a new branch for every Pull Request
    - Include just related commits in this branch
    - Less commits are better, one would be the best (You can squash them.)
    - Always add tests for your feature, if you are not familiar with writing tests, ask for help.
    - Hint: To update your fork with the newest changes, follow `these instructions <https://stackoverflow.com/a/7244456/2947505>`_.

.. _Github Issues: https://github.com/eruvanos/openbrokerapi/issues

.. |Build Status| image:: https://travis-ci.org/eruvanos/openbrokerapi.svg?branch=master
   :target: https://travis-ci.org/eruvanos/openbrokerapi
.. |Coverage Status| image:: https://coveralls.io/repos/github/eruvanos/openbrokerapi/badge.svg?branch=master
   :target: https://coveralls.io/github/eruvanos/openbrokerapi?branch=master
.. |Known Vulnerabilities| image:: https://snyk.io/test/github/eruvanos/openbrokerapi/badge.svg?targetFile=requirements.txt
   :target: https://snyk.io/test/github/eruvanos/openbrokerapi?targetFile=requirements.txt
.. |PYUP| image:: https://pyup.io/repos/github/eruvanos/openbrokerapi/shield.svg
     :target: https://pyup.io/repos/github/eruvanos/openbrokerapi/
   

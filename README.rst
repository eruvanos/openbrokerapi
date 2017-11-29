|Build Status| |Coverage Status|

Open Broker API
===============

A Python package for building Service Brokers supporting API version 2.13+.

Following `CF Service Broker
API <https://docs.cloudfoundry.org/services/api.html>`__ and `Open
Service Broker API <https://www.openservicebrokerapi.org/>`__

Check out the documentation_.

.. _documentation: http://openbrokerapi.readthedocs.io/en/latest/

Installation
------------

This package is available for Python 3.5+.

.. code:: bash

    pip3 install openbrokerapi

Or install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/eruvanos/openbrokerapi.git

Usage
-----

.. code:: python

    from flask import Flask
    from openbrokerapi import service_broker
    from openbrokerapi.api import *
    from openbrokerapi.log_util import *

    # Implement a service broker by overriding methods of ServiceBroker
    class ExampleService(service_broker.Service):
        def __init__(self):
            super().__init__(
                id='00000000-0000-0000-0000-000000000000',
                name='example-service',
                description='Example Service does nothing',
                bindable=True,
                plans=[
                    ServicePlan(
                        id='00000000-0000-0000-0000-000000000000',
                        name='small',
                        description='example service plan',
                        metadata=None,
                        free=False,
                        bindable=True,
                    ),
                ],
                tags=['example', 'service'],
                requires=None,
                metadata=ServiceMetadata(
                    displayName='Example Service',
                    imageUrl=None,
                    longDescription=None,
                    providerDisplayName=None,
                    documentationUrl=None,
                    supportUrl=None,
                ),
                dashboard_client=None,
                plan_updateable=True,
            )

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

    # Simply start the server
    serve([CustomService()], BrokerCredentials("", ""))

    # or start the server without authentication
    serve(CustomServiceBroker(), None)

    # or register blueprint to your own FlaskApp instance
    app = Flask(__name__)
    logger = basic_config() #  Use root logger with a basic configuration provided by openbrokerapi.log_utils
    openbroker_bp = get_blueprint([CustomService()], BrokerCredentials("",""), logger)
    app.register_blueprint(openbroker_bp)
    app.run("0.0.0.0")

Error Types
-----------

Openbrokerapi defines a handful of error types in errors.py for some
common error cases that your service broker may encounter. Raise these
from your ServiceBroker methods where appropriate, and openbrokerapi
will do the "right thing" (™), and give Cloud Foundry an appropriate
status code, as per the Service Broker API specification.

Internal Notes
--------------

- Context object from update 2.12 and 2.13 is ignored. This can change, when an update removes the redundant fields.

Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/eruvanos/openbrokerapi/issues>`__

.. |Build Status| image:: https://travis-ci.org/eruvanos/openbrokerapi.svg?branch=master
   :target: https://travis-ci.org/eruvanos/openbrokerapi
.. |Coverage Status| image:: https://coveralls.io/repos/github/eruvanos/openbrokerapi/badge.svg?branch=master
   :target: https://coveralls.io/github/eruvanos/openbrokerapi?branch=master

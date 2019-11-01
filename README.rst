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

This package is available for Python 3.6+.

.. code:: bash

    pip3 install openbrokerapi

    # including gevent as server
    pip3 install openbrokerapi[gevent]
    
    # recommended production setup
    pip3 install openbrokerapi[gunicorn]

Or install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/eruvanos/openbrokerapi.git

Usage
-----

You can start with a `skeleton project <https://github.com/eruvanos/openbrokerapi-skeleton>`__ or just from scratch.

.. code:: python

    from typing import Union, List

    import openbrokerapi
    from openbrokerapi import api
    from openbrokerapi.api import ServiceBroker
    from openbrokerapi.catalog import ServicePlan
    from openbrokerapi.service_broker import (
        Service,
        ProvisionDetails,
        ProvisionedServiceSpec,
        DeprovisionDetails,
        DeprovisionServiceSpec
    )


    class MyServiceBroker(ServiceBroker):
        def catalog(self) -> Union[Service, List[Service]]:
            return Service(
                id='service id',
                name='service name',
                description='service description',
                bindable=False,
                plans=[
                    ServicePlan(
                        id='plan id',
                        name='plan name',
                        description='plan description',
                    )
                ]
            )

        def provision(self,
                      instance_id: str,
                      details: ProvisionDetails,
                      async_allowed: bool,
                      **kwargs) -> ProvisionedServiceSpec:
            # Create service instance
            # ...

            return ProvisionedServiceSpec()

        def deprovision(self,
                        instance_id: str,
                        details: DeprovisionDetails,
                        async_allowed: bool,
                        **kwargs) -> DeprovisionServiceSpec:
            # Delete service instance
            # ...

            return DeprovisionServiceSpec(is_async=False)

    print('Start server on 127.0.0.1:5000')
    print('Check the catalog at:')
    print('> curl 127.0.0.1:5000/v2/catalog -H "X-Broker-API-Version: 2.14"')
    api.serve(MyServiceBroker(), None)

    # Simply start the server
    # api.serve(ExampleServiceBroker(), api.BrokerCredentials("", ""))

    # or start the server without authentication
    # api.serve(ExampleServiceBroker(), None)

    # or start the server with multiple authentication
    # api.serve(ExampleServiceBroker(), [api.BrokerCredentials("", ""), api.BrokerCredentials("", "")])

    # or with multiple service brokers and multiple credentials
    # api.serve_multiple([ExampleServiceBroker(), ExampleServiceBroker()], [api.BrokerCredentials("", ""), api.BrokerCredentials("", "")])

    # or register blueprint to your own FlaskApp instance
    # app = Flask(__name__)
    # logger = basic_config()  # Use root logger with a basic configuration provided by openbrokerapi.log_utils
    # openbroker_bp = api.get_blueprint(ExampleServiceBroker(), api.BrokerCredentials("", ""), logger)
    # app.register_blueprint(openbroker_bp)
    # app.run("0.0.0.0")

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
   

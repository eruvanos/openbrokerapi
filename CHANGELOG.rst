Changelog
=============

**v0.5.0**
  - error handling fixed for ServiceExceptions
  - support 200-OK as provision and bind responses `[issue #1]`_

    - instead of 'is_async' flag an enumeration is used

.. _[issue #1]: https://github.com/eruvanos/openbrokerapi/issues/1

**v0.4.1**
  - support Python 3.5+

**v0.4.0**
  - remove unused response classes
  - ProvisionedServiceSpec: do not require optional fields
  - DeprovisionServiceSpec: do not require optional fields
  - LastOperation: do not require optional fields
  - update to openbrokerapi 2.13 (minimal required)
  - correct some required vs non required fields

**v0.3.1**
  - fix api.serve

**v0.3**
  - use LastOperationResponse for last\_operation response
  - fix: catalog response was not convertible to json
  - fix: not required fields were still in catalog response
  - add missing tests for catalog endpoint
  - support for VolumeMounts is tested

**v0.2**
  - improve testing
  - fix: Bind and update getting dict instead of expected objects
  - support async for provision, update and deprovision
  - Handle unexpected exception with global error\_handler (responding
    with 500)
  - get\_blueprint() now expects a logger
  - add log\_utils with basic\_config()

**v0.1**
  -  initial version
  -  supported operations
  -  provision
  -  update
  -  bind
  -  unbind
  -  deprovision

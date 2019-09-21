Changelog
=============

**v4.0**
  - Extract routing mechanism into a `Router` class
  - Clean `ServiceBroker` interface

**Incompatibility**
  - Changed parameter order in UnbindDetails, DeprovisionDetails
  - Changed parameter name of provision


**v3.2**
  - Add shareable to ServiceMetaData
  - 501 to unimplemented broker actions  #41
  - Fixed: AttributeError in broker without creds #43
  - Add `ErrInvalidParameters` to respond with `400` for malformed or missing mandatory data #49
  - Support for custom Metadata fields. #47

**v3.1.x**
  - Fix typos
  - Add checks for Content-Type
  - Use `gevent` instead of `app.run`
  - Originating-Identity available (thx to #10 redorff)
  - Context dict available (thx to #10 redorff)
  - Support multiple credentials (thx to #10 redorff)
  - Service update can return dashboard_url
  - Return 400 also when body not parsable
  - Improve docs

**v2.0.0**
  - Refactor API

**v1.0.0**
  - permit to run a broker without authentication
  - Support multiple services with one broker

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

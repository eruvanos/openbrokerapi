Changelog
=============

**4.7.0**
  - Update to latest dependencies (incl Flask >=3)


**4.6.0**
  - Update dependencies

    - Removing types-urllib3 (1.26.25.14)
    - Updating charset-normalizer (3.2.0 -> 3.3.0)
    - Updating urllib3 (2.0.4 -> 2.0.6)
    - Updating zipp (3.16.2 -> 3.17.0)
    - Updating packaging (23.1 -> 23.2)
    - Updating blinker (1.6.2 -> 1.6.3)
    - Updating filelock (3.12.2 -> 3.12.4)
    - Updating platformdirs (3.10.0 -> 3.11.0)
    - Updating setuptools (68.1.2 -> 68.2.2)
    - Updating werkzeug (2.3.7 -> 3.0.0)
    - Updating identify (2.5.27 -> 2.5.30)
    - Updating pluggy (1.2.0 -> 1.3.0)
    - Updating typing-extensions (4.7.1 -> 4.8.0)
    - Updating virtualenv (20.24.3 -> 20.24.5)
    - Updating black (23.7.0 -> 23.9.1)
    - Updating mypy (1.5.1 -> 1.6.0)
    - Updating pre-commit (3.3.3 -> 3.5.0)
    - Updating pytest (7.4.0 -> 7.4.2)
    - Updating types-requests (2.31.0.2 -> 2.31.0.9)


**4.5.8**
  - Update dependencies (Werkzeug=2.3.7, Flask=2.3.3, ...)

**4.5.7**
  - minor improvements

**4.5.6**
  - Improve documentation for Authenticator and rename to BrokerAuthenticator. Keep old names for now.

**4.5.5**
  - Update Flask to 2.3.2: [CVE-2023-30861](https://github.com/advisories/GHSA-m2qf-hxjv-5gpq)
  - Update pytest from 7.2.1 to 7.3.1
  - Use trusted provider flow to publish to pypi

> Releases 4.5.1-4 were used to test the new GitHub workflow and are only pushed to Test-PYPI

**4.5**
  - Drop Python 3.7 support
  - Update dependencies

**v4.4**
  - Provide an option to provide a custom authentication implementing `openbrokerapi.auth.Authenticator`

**v4.3.1**
  - Pass error messages of `ErrBadRequest` to inform the platform about the issue details


**v4.3**
  - Fix [issue 211](https://github.com/eruvanos/openbrokerapi/issues/211) use keyword arguments to call broker functions from api

**v4.2**
  - ErrConcurrentInstanceAccess exception on an instance update, an instance deprovision, a binding or unbinding must return 422 not 500.
  - ErrPlanChangeNotSupported exception must return 400 not 500.
  - last_operation and last_binding_operation forward service and plan identifiers when provided

  - Update dependencies
  - Drop Python 3.6 support
  - Migrate to Poetry

**v4.1**
  - Drop Python 3.5 support
  - Fix ´bind´ in multi broker setup (#117); thx @vaxvms
  - Removing requirement to have a space_guid and an organization_guid (#116); thx @rajahaidar
  - Improve documentation; thx @vaxvms
  - Fix collections.abc deprecation; thx @tammersaleh

**v4.0.2**
  - Introduce new error to return BadRequest
  - Add **kwargs to catalog classes

**v4.0.1**
  - Add gunicorn installation

**v4.0**
  - Extract routing mechanism into a `Router` class
  - Clean `ServiceBroker` interface
  - `gevent` is now optional and can be installed by `pip install openbrokerapi[gevent]`
  - Added endpoint to get last binding operation
  - Introduce `**kwargs` into some signatures to improve backwards compatibility in the future
  - Fixed responses with status 412 don't contain body (https://github.com/pallets/werkzeug/issues/1231)
  - `ServiceBroker` provides methods to fetch instance and binding
  - Provision does not require `organization_guid` and `space_guid` parameters, if they are available in the context object

**Incompatibility**
  - Changed parameter order in `UnbindDetails`, `DeprovisionDetails`
  - Changed parameter name of `ServiceBroker.provision`
  - Removed deprecated `ServicePlanMetaData` (use `ServicePlanMetadata`)
  - Unbind now returns `UnbindSpec`
  - `ServiceBroker.bind` and `ServiceBroker.unbind` now receive `async_allowed` flag

        **Why breaking changes?**

        To catch up with the newest features of the OpenServiceBroker API some breaking changes were neccessary.
        While I was working on the new version I realised that there are a few things I really wanted to fix, which is at the end the reason, for some changes that may not be necessary but nice to have.

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

# Open Service Broker API 2.17 - Missing Features Analysis

This document identifies the differences between the current openbrokerapi implementation (supporting 2.13+) and the OSBAPI 2.17 specification.

## Current Implementation Status
- **Minimum Supported Version**: 2.13
- **Library Version**: 4.7.3
- **Last Updated**: Based on code analysis, implementation seems to support up to ~2.14-2.15 features

## Missing Features from OSBAPI 2.17

### 1. Service Plan Object - New Fields

#### binding_rotatable
**Status**: ❌ Missing
**Spec Reference**: Service Plan Object
**Description**: Boolean field indicating whether a Service Binding of that Plan supports Service Binding rotation.

```python
# Missing from openbrokerapi/catalog.py ServicePlan class
class ServicePlan:
    def __init__(
        self,
        # ... existing fields ...
        binding_rotatable: Optional[bool] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.binding_rotatable = binding_rotatable  # MISSING
```

#### maximum_polling_duration
**Status**: ❌ Missing
**Spec Reference**: Service Plan Object
**Description**: A duration, in seconds, that the Platform SHOULD use as the Service's maximum polling duration.

```python
# Missing from openbrokerapi/catalog.py ServicePlan class
class ServicePlan:
    def __init__(
        self,
        # ... existing fields ...
        maximum_polling_duration: Optional[int] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.maximum_polling_duration = maximum_polling_duration  # MISSING
```

#### maintenance_info
**Status**: ❌ Missing
**Spec Reference**: Service Plan Object, Maintenance Info Object
**Description**: Maintenance information for a Service Instance which is provisioned using the Service Plan.

```python
# Missing from openbrokerapi/catalog.py
class MaintenanceInfo:
    def __init__(
        self,
        version: str,
        description: Optional[str] = None,
        **kwargs
    ):
        self.version = version
        self.description = description
        self.__dict__.update(kwargs)

# Missing from ServicePlan class
class ServicePlan:
    def __init__(
        self,
        # ... existing fields ...
        maintenance_info: Optional[MaintenanceInfo] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.maintenance_info = maintenance_info  # MISSING
```

### 2. Service Object - New Fields

#### allow_context_updates
**Status**: ❌ Missing
**Spec Reference**: Service Offering Object
**Description**: Specifies whether a Service Instance supports Update requests when contextual data for the Service Instance in the Platform changes.

```python
# Missing from openbrokerapi/service_broker.py Service class
class Service:
    def __init__(
        self,
        # ... existing fields ...
        allow_context_updates: Optional[bool] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.allow_context_updates = allow_context_updates  # MISSING
```

### 3. Binding - Service Binding Rotation

#### predecessor_binding_id
**Status**: ❌ Missing
**Spec Reference**: Binding Request (Rotating a Service Binding)
**Description**: Field for creating successor bindings in Service Binding rotation.

```python
# Missing from openbrokerapi/service_broker.py BindDetails class
class BindDetails:
    def __init__(
        self,
        # ... existing fields ...
        predecessor_binding_id: Optional[str] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.predecessor_binding_id = predecessor_binding_id  # MISSING
```

### 4. Binding Metadata Object

#### metadata field with expires_at and renew_before
**Status**: ❌ Missing
**Spec Reference**: Binding Response, Binding Metadata Object
**Description**: Metadata for Service Bindings including expiration information.

```python
# Missing from openbrokerapi/service_broker.py or response.py
class BindingMetadata:
    def __init__(
        self,
        expires_at: Optional[str] = None,
        renew_before: Optional[str] = None,
        **kwargs
    ):
        self.expires_at = expires_at
        self.renew_before = renew_before
        self.__dict__.update(kwargs)

# Missing from Binding and response classes
class Binding:
    def __init__(
        self,
        # ... existing fields ...
        metadata: Optional[BindingMetadata] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.metadata = metadata  # MISSING
```

### 5. Endpoint Object

#### endpoints array
**Status**: ❌ Missing
**Spec Reference**: Binding Response, Endpoint Object
**Description**: Network endpoints that the Application uses to connect to the Service Instance.

```python
# Missing from openbrokerapi/service_broker.py
class Endpoint:
    def __init__(
        self,
        host: str,
        ports: List[str],
        protocol: Optional[str] = "tcp",
        **kwargs
    ):
        self.host = host
        self.ports = ports
        self.protocol = protocol
        self.__dict__.update(kwargs)

# Missing from Binding and response classes
class Binding:
    def __init__(
        self,
        # ... existing fields ...
        endpoints: Optional[List[Endpoint]] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.endpoints = endpoints  # MISSING
```

### 6. Error Codes

#### MaintenanceInfoConflict
**Status**: ❌ Missing
**Spec Reference**: Service Broker Errors
**Description**: Error code for when maintenance_info.version field provided in request doesn't match catalog.

```python
# Missing from openbrokerapi/errors.py
class ErrMaintenanceInfoConflict(ServiceException):
    def __init__(self):
        super().__init__("MaintenanceInfoConflict")
```

### 7. HTTP Headers - Retry-After

#### Retry-After header support
**Status**: ❌ Missing
**Spec Reference**: Polling Last Operation endpoints
**Description**: Support for Retry-After HTTP header in last operation responses.

```python
# Missing from openbrokerapi/response.py LastOperationResponse
class LastOperationResponse:
    def __init__(
        self,
        state: OperationState,
        description: str,
        retry_after: Optional[int] = None,  # MISSING
        # ... other fields ...
    ):
        # ... existing init code ...
        self.retry_after = retry_after  # MISSING
```

### 8. Provision Request - maintenance_info field

#### maintenance_info in ProvisionDetails
**Status**: ❌ Missing
**Spec Reference**: Provisioning Request
**Description**: Maintenance information in provision requests.

```python
# Missing from openbrokerapi/service_broker.py ProvisionDetails class
class ProvisionDetails:
    def __init__(
        self,
        # ... existing fields ...
        maintenance_info: Optional[dict] = None,  # MISSING (should be MaintenanceInfo)
        # ...
    ):
        # ... existing init code ...
        self.maintenance_info = maintenance_info  # MISSING
```

### 9. Update Request - maintenance_info field

#### maintenance_info in UpdateDetails
**Status**: ❌ Missing
**Spec Reference**: Updating a Service Instance Request
**Description**: Maintenance information in update requests.

```python
# Missing from openbrokerapi/service_broker.py UpdateDetails class
class UpdateDetails:
    def __init__(
        self,
        # ... existing fields ...
        maintenance_info: Optional[dict] = None,  # MISSING (should be MaintenanceInfo)
        # ...
    ):
        # ... existing init code ...
        self.maintenance_info = maintenance_info  # MISSING
```

### 10. Service Instance Metadata

#### Service Instance metadata object
**Status**: ❌ Missing
**Spec Reference**: Provisioning Response, Update Response, Fetch Service Instance Response
**Description**: Metadata object for Service Instances with labels and attributes.

```python
# Missing from openbrokerapi/service_broker.py or response.py
class ServiceInstanceMetadata:
    def __init__(
        self,
        labels: Optional[dict] = None,
        attributes: Optional[dict] = None,
        **kwargs
    ):
        self.labels = labels
        self.attributes = attributes
        self.__dict__.update(kwargs)

# Missing from response classes
class ProvisioningResponse:
    def __init__(
        self,
        # ... existing fields ...
        metadata: Optional[ServiceInstanceMetadata] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.metadata = metadata  # MISSING
```

### 11. Previous Values Object - maintenance_info field

#### maintenance_info in PreviousValues
**Status**: ❌ Missing
**Spec Reference**: Previous Values Object
**Description**: Maintenance information in previous values for update requests.

```python
# Missing from openbrokerapi/service_broker.py PreviousValues class
class PreviousValues:
    def __init__(
        self,
        # ... existing fields ...
        maintenance_info: Optional[dict] = None,  # MISSING (should be MaintenanceInfo)
        # ...
    ):
        # ... existing init code ...
        self.maintenance_info = maintenance_info  # MISSING
```

### 12. Fetch Service Instance Response - maintenance_info field

#### maintenance_info in GetInstanceDetailsSpec
**Status**: ❌ Missing
**Spec Reference**: Fetching a Service Instance Response
**Description**: Maintenance information in service instance fetch responses.

```python
# Missing from openbrokerapi/service_broker.py GetInstanceDetailsSpec class
class GetInstanceDetailsSpec:
    def __init__(
        self,
        # ... existing fields ...
        maintenance_info: Optional[dict] = None,  # MISSING (should be MaintenanceInfo)
        metadata: Optional[ServiceInstanceMetadata] = None,  # MISSING
        # ...
    ):
        # ... existing init code ...
        self.maintenance_info = maintenance_info  # MISSING
        self.metadata = metadata  # MISSING
```

## Summary of Changes Needed

### High Priority (Core 2.17 Features)
1. **Service Binding Rotation** - Add `binding_rotatable` and `predecessor_binding_id`
2. **Maintenance Info Object** - Complete implementation across all relevant classes
3. **Service Instance Metadata** - Add metadata support for service instances
4. **Binding Metadata** - Add metadata with expiration fields for bindings
5. **MaintenanceInfoConflict Error** - Add new error code

### Medium Priority (Enhancement Features)  
6. **Endpoints Array** - Add network endpoint information to bindings
7. **Allow Context Updates** - Add service-level flag for context update support
8. **Maximum Polling Duration** - Add per-plan polling duration limits
9. **Retry-After Headers** - Add retry timing headers to last operation responses

### Implementation Notes
- Most missing features are additive and should not break backward compatibility
- The `maintenance_info` field appears in multiple places and needs a consistent `MaintenanceInfo` class
- Service binding rotation is a significant new feature that requires careful implementation
- All new fields should be optional to maintain backward compatibility
- Tests will need to be added for all new features

### Files That Need Updates
- `openbrokerapi/catalog.py` - ServicePlan updates
- `openbrokerapi/service_broker.py` - Multiple class updates
- `openbrokerapi/response.py` - Response class updates  
- `openbrokerapi/errors.py` - New error class
- `openbrokerapi/api.py` - Request handling updates
- Test files - Comprehensive test coverage for new features
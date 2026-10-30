# TODO - OSBAPI Spec Implementation

## Status: Based on OSBAPI 2.17 Analysis

### Existing TODO Items (Legacy)
- 379: Catalog/Plan - plan_updateable ✅ **IMPLEMENTED**
- 480: Catalog/Plan - maximum_polling_duration ❌ **MISSING in 2.17**
- 481: Catalog/Plan - maintenance_info ❌ **MISSING in 2.17** 
- 481: Catalog/Plan - maintenance_info (duplicate)

- 340: Error codes - MaintenanceInfoConflict ❌ **MISSING in 2.17**
- 521f: Maintenance Info Object ❌ **MISSING in 2.17**
- 541: Catalog - allow_context_updates ❌ **MISSING in 2.17**
- 789: LastOperation - Retry-After Header ❌ **MISSING in 2.17**
- 871: LastBindingOperation - Retry-After Header ❌ **MISSING in 2.17**
- 931: Provision - maintenance_info ❌ **MISSING in 2.17**
- 1073: Update - profile#cloud-foundry-context-object ❓ **NEEDS REVIEW**
- 1121: Update - maintenance_info ❌ **MISSING in 2.17**
- 1428: Bind - Endpoints ❌ **MISSING in 2.17**
- 1454: Bind - Endpoint Object ❌ **MISSING in 2.17**
- 1545: FetchBind - Endpoint Object ❌ **MISSING in 2.17**

### Additional Items Found in 2.17 Spec Analysis
- ServicePlan.binding_rotatable ❌ **MISSING in 2.17**
- BindDetails.predecessor_binding_id ❌ **MISSING in 2.17**
- BindingMetadata object (expires_at, renew_before) ❌ **MISSING in 2.17**
- ServiceInstanceMetadata object (labels, attributes) ❌ **MISSING in 2.17**
- ProvisionDetails.maintenance_info ❌ **MISSING in 2.17**
- UpdateDetails.maintenance_info ❌ **MISSING in 2.17**
- PreviousValues.maintenance_info ❌ **MISSING in 2.17**
- GetInstanceDetailsSpec.maintenance_info ❌ **MISSING in 2.17**
- GetInstanceDetailsSpec.metadata ❌ **MISSING in 2.17**

## See OSBAPI_2_17_ANALYSIS.md for detailed implementation guidance

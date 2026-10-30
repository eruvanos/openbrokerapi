from openbrokerapi.catalog import ServicePlan, MaintenanceInfo
from openbrokerapi.helper import _to_dict
from openbrokerapi.service_broker import Service


def plan(**kw):
    return ServicePlan("p", "plan", "desc", **kw)


def service(**kw):
    return Service("s", "svc", "desc", True, [plan()], **kw)


def test_unset_fields_not_serialized():
    d = _to_dict(service())
    for k in ["allow_context_updates"]:
        assert k not in d
    for k in ["plan_updateable", "maximum_polling_duration", "maintenance_info", "binding_rotatable"]:
        assert k not in d["plans"][0]


def test_explicit_equals_kwargs():
    kw = {
        "plan_updateable": True,
        "maximum_polling_duration": 120,
        "maintenance_info": {"version": "1.0"},
        "binding_rotatable": True,
    }
    expected = {
        "id": "p",
        "name": "plan",
        "description": "desc",
        "plan_updateable": True,
        "maximum_polling_duration": 120,
        "maintenance_info": {"version": "1.0"},
        "binding_rotatable": True,
    }
    assert _to_dict(plan(**kw)) == expected


def test_maintenance_info_object():
    p = plan(maintenance_info=MaintenanceInfo("2.0", "desc"))
    assert _to_dict(p)["maintenance_info"] == {"version": "2.0", "description": "desc"}


def test_service_allow_context_updates():
    assert _to_dict(service(allow_context_updates=True))["allow_context_updates"] is True
    assert _to_dict(service(allow_context_updates=False))["allow_context_updates"] is False

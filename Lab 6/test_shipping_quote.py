import pytest
from shipping_quote import process_shipments, monitor_container_pressures

# Example test case:
def test_single_ground_shipment():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "express_priority": False,
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"

def test_invalid_shipments_and_handling_fee():
    with pytest.raises(ValueError, match="Invalid shipments list or handling fee"):
        process_shipments({}, 20.0)

    with pytest.raises(ValueError, match="Invalid shipments list or handling fee"):
        process_shipments([], -1.0)


def test_air_heavy_shipment_with_express_priority():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "air",
            "express_priority": True,
            "packages": [{"weight_kg": 40, "is_hazmat": False}],
        }
    ]

    assert process_shipments(shipments, 10.0) == {
        "total_quote": 912.5,
        "status": "CLEARED",
    }


def test_unapproved_and_unknown_mode_shipments_are_skipped():
    shipments = [
        {"manifest_approved": False, "mode": "air"},
        {"manifest_approved": True, "mode": "sea"},
    ]

    assert process_shipments(shipments, 10.0) == {
        "total_quote": 0.0,
        "status": "NO_CARGO",
    }


def test_invalid_weight_and_hazmat_parcels_are_rejected():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [
                {"weight_kg": 0, "is_hazmat": False},
                {"weight_kg": 5, "is_hazmat": True},
            ],
        }
    ]

    assert process_shipments(shipments, 20.0) == {
        "total_quote": 70.0,
        "status": "CLEARED",
    }


def test_fragile_hazmat_parcel_stops_shipment_cost():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": True,
            "packages": [{"weight_kg": 5, "is_hazmat": True}],
        }
    ]

    assert process_shipments(shipments, 20.0) == {
        "total_quote": 0.0,
        "status": "NO_CARGO",
    }


def test_stable_pressure_logs():
    assert monitor_container_pressures([[14.0, 13.5, 14.0]]) == "STABLE"
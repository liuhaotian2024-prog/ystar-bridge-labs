from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_host_network_probe(root: Path | None = None) -> dict:
    base = root or core.BRIDGE_ROOT
    return {
        "inventory": core.build_host_network_probe_inventory(base),
        "sandbox_dns_probe": core.build_sandbox_dns_probe_result(base),
        "delivery_bridge_probe_request": core.build_delivery_bridge_network_probe_request(base),
        "delivery_bridge_probe_result": core.build_delivery_bridge_network_probe_result(base),
        "blocker_classification": core.build_public_read_blocker_classification(base),
    }


def write_host_network_probe(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_host_network_probe(root)
    core.write_json(root, "operations/external_validation/e62_host_network_probe_inventory.json", data["inventory"])
    core.write_json(root, "operations/external_validation/e62_sandbox_dns_probe_result.json", data["sandbox_dns_probe"])
    core.write_json(root, "operations/external_validation/e62_delivery_bridge_network_probe_request.json", data["delivery_bridge_probe_request"])
    core.write_json(root, "operations/external_validation/e62_delivery_bridge_network_probe_result.json", data["delivery_bridge_probe_result"])
    core.write_json(root, "operations/external_validation/e62_public_read_blocker_classification.json", data["blocker_classification"])
    return data

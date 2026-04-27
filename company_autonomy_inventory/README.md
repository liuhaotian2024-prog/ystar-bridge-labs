# Company Autonomy Inventory

This L4.1 pack maps existing company/runtime assets into an autonomy capability
inventory and governed action registry candidate set.

The pack is discovery-only. It does not run discovered tools, execute actions,
write CIEU, write brain or memory, approve candidates, or read raw runtime
artifacts.

Build the generated inventory:

```bash
python3 company_autonomy_inventory/tools/build_company_autonomy_inventory.py
```

The goal is a commercial AI agent company that can observe resources, understand
constraints, choose governed tools, and eventually perform real work through
safe action channels. This milestone maps what already exists and keeps every
action candidate disabled.

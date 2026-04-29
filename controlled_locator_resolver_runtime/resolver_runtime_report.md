# Resolver Runtime Report

The portable runtime is implemented in `controlled_locator_resolver.py`.
It attempts one local seed registry lookup, then checks the environment-gated
search resolver only if explicitly enabled, then returns a disabled blocked
result. The default L6.10U run used no network and did not fabricate a locator.

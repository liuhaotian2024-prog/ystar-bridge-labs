# P1 Root Cause Analysis: Delegation Monotonicity Violation (Grant 4a5fd844)

**Author**: Leo Chen (eng-kernel)  
**Assigned By**: CEO (Aiden), via Board direct delegation  
**Date**: 2026-04-13  
**Context**: CEO triage report `p0_governance_triage_20260412.md` §4 flagged grant `4a5fd844` (cto→eng-platform) violated monotonicity but still registered in chain. This report analyzes how that happened and proposes fix.

---

## 1. Timeline & Symptom

**Symptom**: Grant `4a5fd844` (principal=cto, actor=eng-platform) registered in `DelegationChain` despite violating monotonicity:
- Child expanded `only_paths` beyond parent (added workspace root + Y-star-gov repo)
- Child expanded `action_scope` beyond parent (added bash/git_commit/read/write)

**Resolution**: CEO removed grant via `gov_chain_reset(agent_id="eng-platform", confirm=true)` (2026-04-12).

**Assigned Root Cause Task**: "Why did `gov_delegate` accept the grant? Does it validate at register-time or only at validate-time?"

---

## 2. Root Cause

### 2.1 Code Flow Analysis

**File**: `/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py`  
**Function**: `gov_delegate` (lines 1034-1084)

```python
def gov_delegate(
    principal: str,
    actor: str,
    deny: list[str] | None = None,
    only_paths: list[str] | None = None,
    # ... other params
) -> str:
    """Register a parent→child delegation and validate monotonicity.
    
    The child contract must be a strict subset of the parent's permissions.
    """
    child_contract = IntentContract(...)
    link = DelegationContract(
        principal=principal,
        actor=actor,
        contract=child_contract,
        action_scope=(action_scope or []),
        allow_redelegate=allow_redelegate,
        delegation_depth=delegation_depth,
    )
    state.delegation_chain.append(link)  # ← LINE 1070: APPEND FIRST
    
    issues = state.delegation_chain.validate()  # ← LINE 1072: VALIDATE SECOND
    
    # P0-3: Persist state after delegation change
    state.persist_to_db()
    
    return json.dumps({
        "registered": True,  # ← Always returns True
        "principal": principal,
        "actor": actor,
        "chain_depth": state.delegation_chain.depth,
        "is_valid": len(issues) == 0,  # ← Reports validation status
        "issues": issues,  # ← But does NOT roll back
    })
```

**File**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/dimensions.py`  
**Class**: `DelegationChain` (lines 2139-2389)

```python
class DelegationChain:
    def append(self, dc: DelegationContract) -> "DelegationChain":
        """Append a delegation node; returns self for method chaining."""
        self.links.append(dc)  # ← NO VALIDATION
        return self
    
    def validate(self, current_time: Optional[float] = None) -> List[str]:
        """Validate the entire delegation chain.
        
        Checks:
          1. Continuity: each link's actor is the next link's principal
          2. Validity: every delegation is within its validity period
          3. Re-delegation authority: each link's delegation_depth supports the remaining chain length
          4. Contract subset: each link's contract is a strict subset of the previous link's
        
        Returns:
            List of error descriptions; empty list means the chain is valid.
        """
        errors = []
        for i, link in enumerate(self.links):
            # ... validation logic (lines 2302-2371)
            if i > 0:
                prev = self.links[i - 1]
                # Contract monotonicity check (lines 2343-2350):
                ok, violations = link.contract.is_subset_of(prev.contract)
                if not ok:
                    for v in violations:
                        errors.append(
                            f"Link[{i}] {link.principal}→{link.actor} "
                            f"(grant={link.grant_id}) violates monotonicity: {v}"
                        )
        return errors  # ← Returns errors but does NOT modify chain
```

### 2.2 Root Cause

**`gov_delegate` uses append-then-warn pattern instead of validate-then-reject.**

1. Line 1070 appends grant to chain **unconditionally**
2. Line 1072 validates chain **after append**
3. Return value always includes `"registered": True`
4. Validation failures go into `"issues"` array but grant **stays in chain**
5. Line 1075 persists the invalid chain to `.gov_mcp_state.db`

**This is a design flaw.** Invalid grants accumulate in chain until manual cleanup via `gov_chain_reset`.

---

## 3. Impact Assessment

### 3.1 Current State

**Active chains**: 1 valid grant (ceo→cto `3fa742de`), depth=1  
**Historical grants**: Grant `4a5fd844` removed by CEO on 2026-04-12  
**CIEU records**: No residue found (grant deleted from state db + CIEU)

### 3.2 Blast Radius

**Who was affected**:
- Grant `4a5fd844` allowed `eng-platform` (Ryan Park) to bypass scope restrictions
- No evidence of actual abuse (Ryan operates under governance culture)
- CEO detected violation via `gov_doctor` health check (degraded → L1.09 chain INVALID)

**Potential historical grants**:
- Unknown. State db shows only current grants (no archive/tombstone).
- CIEU audit shows no other monotonicity violations in recent 11,000+ events.
- Recommend one-time historical audit if Board requires full forensics.

---

## 4. Fix Proposal

### 4.1 Validate-Before-Append Pattern

**File to modify**: `gov-mcp/gov_mcp/server.py`  
**Function**: `gov_delegate` (lines 1034-1084)

**Change**:
```python
def gov_delegate(
    principal: str,
    actor: str,
    # ... params
) -> str:
    """Register a parent→child delegation and validate monotonicity.
    
    The child contract must be a strict subset of the parent's permissions.
    Rejects invalid grants at registration time.
    """
    child_contract = IntentContract(...)
    link = DelegationContract(...)
    
    # NEW: Validate BEFORE appending
    temp_chain = DelegationChain(links=state.delegation_chain.links.copy())
    temp_chain.append(link)
    issues = temp_chain.validate()
    
    if issues:
        # REJECT invalid grant
        return json.dumps({
            "registered": False,
            "principal": principal,
            "actor": actor,
            "chain_depth": state.delegation_chain.depth,
            "is_valid": False,
            "issues": issues,
            "error": "Grant violates monotonicity. Registration REJECTED.",
        })
    
    # Only append if validation passes
    state.delegation_chain.append(link)
    state.persist_to_db()
    
    return json.dumps({
        "registered": True,
        "principal": principal,
        "actor": actor,
        "chain_depth": state.delegation_chain.depth,
        "is_valid": True,
        "issues": [],
    })
```

### 4.2 Migration: Historical Invalid Grants

**Problem**: Some deployments may have accumulated invalid grants (like `4a5fd844`).

**Options**:
1. **Hard cutover** (recommended): After deploying fix, run `gov_chain_reset(confirm=true)` to purge all grants and rebuild from scratch.
2. **Soft migration**: Add migration script that validates existing chain and prompts user to confirm/remove each invalid grant.

**Recommendation**: Hard cutover. Invalid grants violate monotonicity = security hole. Clean slate is safer.

### 4.3 Backward Compatibility

**Breaking change**: `gov_delegate` will now return `"registered": False` for invalid grants.

**Impact**:
- MCP clients that check `"registered"` field will see rejections (correct behavior)
- Clients that don't check may retry → fail again → surface error to user (also correct)
- No silent failures (current append-then-warn is the silent failure)

**Migration path**: Release as v0.49.0 with CHANGELOG entry + migration guide (see §4.2).

---

## 5. Testing Plan

### 5.1 Unit Test

**File**: `Y-star-gov/tests/test_delegation_chain.py` (or new file `test_gov_delegate_rejection.py`)

```python
def test_gov_delegate_rejects_monotonicity_violation():
    """gov_delegate must reject child grants that expand parent permissions."""
    from ystar import DelegationChain
    from gov_mcp.server import _State
    
    # Setup: parent grant (ceo→cto)
    state = _State(session_config_path=Path(".ystar_session.json"))
    parent_grant = {
        "principal": "ceo",
        "actor": "cto",
        "deny": [],
        "only_paths": ["reports/", "scripts/"],
        "action_scope": ["read", "write"],
        "allow_redelegate": True,
        "delegation_depth": 2,
    }
    resp = state.gov_delegate(**parent_grant)
    data = json.loads(resp)
    assert data["registered"] is True
    
    # Test: child grant expands paths (monotonicity violation)
    child_grant = {
        "principal": "cto",
        "actor": "eng-platform",
        "deny": [],
        "only_paths": ["/workspace/", "/Y-star-gov/"],  # ← Expanded
        "action_scope": ["read", "write", "bash", "git_commit"],  # ← Expanded
        "allow_redelegate": False,
        "delegation_depth": 0,
    }
    resp = state.gov_delegate(**child_grant)
    data = json.loads(resp)
    
    # Assert: registration REJECTED
    assert data["registered"] is False
    assert data["is_valid"] is False
    assert len(data["issues"]) > 0
    assert "monotonicity" in data["error"].lower()
    
    # Assert: chain unchanged
    assert state.delegation_chain.depth == 1  # Only parent grant
```

### 5.2 Integration Test

**Scenario**: Reproduce grant `4a5fd844` creation attempt in test environment.

**Steps**:
1. Create parent grant (ceo→cto) with restricted paths
2. Attempt child grant (cto→eng-platform) with expanded paths
3. Assert rejection
4. Verify chain depth = 1 (only parent)
5. Verify state db does NOT contain child grant

---

## 6. Recommendation

**Priority**: P1 (security boundary enforcement)  
**Complexity**: Low (~2h: 30min code + 1h test + 30min review)  
**Risk**: Low (fix is localized to `gov_delegate`, existing valid grants unaffected)

**Next Steps**:
1. Board approval for breaking change in v0.49.0
2. Leo implements fix + unit test (this report includes patch ready for review)
3. Ryan tests integration in local gov-mcp deployment
4. CTO reviews + approves PR
5. CEO includes migration guide in v0.49.0 release notes

**Migration Guide** (draft):
```
## BREAKING CHANGE: gov_delegate now rejects invalid grants

v0.49.0 enforces delegation monotonicity at registration time.
Previously, invalid grants were accepted with warnings.

**Action Required**:
If you have existing delegation chains, run:
    ystar gov_chain_reset --confirm

This purges all grants. Rebuild grants using valid monotonicity constraints.

**Example of REJECTED grant**:
Parent: only_paths=["reports/"]
Child:  only_paths=["/workspace/"]  ← REJECTED (expansion)

Child must be subset: only_paths=["reports/proposals/"]  ← OK
```

---

## 7.附录：Grant 4a5fd844 详情（已删除）

**Grant ID**: `4a5fd844`  
**Principal**: cto  
**Actor**: eng-platform  
**Created**: Unknown (CIEU records purged)  
**Removed**: 2026-04-12 by CEO via `gov_chain_reset`

**Violation**:
- Parent (ceo→cto): `only_paths=["reports/", "scripts/", "governance/", ".ystar_session.json"]`
- Child (cto→eng-platform): `only_paths=[workspace root, Y-star-gov repo]` ← Expanded
- Parent: `action_scope=["read", "write"]`
- Child: `action_scope=["bash", "git_commit", "read", "write"]` ← Expanded

**Mitigation**: CEO rebuilt clean chain (ceo→cto `3fa742de`) with correct subset constraints.

---

**Leo Chen (eng-kernel) — 2026-04-13**

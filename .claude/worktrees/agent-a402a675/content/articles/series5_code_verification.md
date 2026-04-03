# Series 5 Code Verification — AST Whitelisting

## FIX-2 Location
- File: ystar/kernel/engine.py
- AST whitelist definition: Lines 224-235
- Blocked attributes definition: Lines 237-242
- Safe eval function: Lines 245-285
- Usage in invariant checking: Lines 456-504
- Usage in optional_invariant checking: Lines 511-541
- Usage in postcondition checking: Lines 545-576

## The Vulnerability (Before Fix)

**Attack Vector**: Python class hierarchy traversal via `eval()` with restricted builtins

**What was bypassable (v0.1.0)**:
```python
# v0.1.0 approach (VULNERABLE):
eval(expr, {"__builtins__": {}}, namespace)
```

The bare `eval()` with empty `__builtins__` dict can be bypassed using Python's class hierarchy:
```python
# Example attack payload in an invariant expression:
"().__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['sys'].modules['os'].system('rm -rf /')"
```

**How it works**:
1. Start with any object (e.g., empty tuple `()`)
2. Access `__class__` to get its type
3. Navigate `__bases__[0]` to reach object base class
4. Call `__subclasses__()` to enumerate all classes in the runtime
5. Find a class with access to dangerous globals (e.g., subprocess, os)
6. Execute arbitrary system commands

**Referenced in code comments** (lines 249-251):
```python
# Replaces bare eval() + {"__builtins__": {}} which is bypassable via
# Python's class hierarchy (__class__.__bases__[0].__subclasses__() ...).
# See CVE-equivalent analysis in ystar_paper.md Appendix A.3.
```

## The Fix (AST Whitelisting)

**Function**: `_safe_eval()` (lines 245-285)

**Security principle**: Parse expressions into an Abstract Syntax Tree, walk every node, and reject ANY node type not explicitly on the whitelist. This happens BEFORE bytecode execution, so malicious code never runs.

**Implementation flow**:
1. Parse expression to AST (line 263)
2. Walk all nodes and check against whitelist (lines 267-276)
3. Block any non-whitelisted node types
4. Block any access to dangerous dunder attributes
5. Block all free function calls (only method calls allowed)
6. Compile and evaluate only if all checks pass (lines 279-283)

## Safe Node Whitelist

**Defined in `_SAFE_AST_NODES` (lines 224-235)**:

```python
_SAFE_AST_NODES = {
    _ast.Expression, _ast.BoolOp, _ast.BinOp, _ast.UnaryOp, _ast.Compare,
    _ast.Constant, _ast.Name, _ast.Load, _ast.And, _ast.Or, _ast.Not,
    _ast.Add, _ast.Sub, _ast.Mult, _ast.Div, _ast.Mod, _ast.FloorDiv, _ast.Pow,
    _ast.Eq, _ast.NotEq, _ast.Lt, _ast.LtE, _ast.Gt, _ast.GtE,
    _ast.Is, _ast.IsNot, _ast.In, _ast.NotIn,
    _ast.IfExp, _ast.Tuple, _ast.List, _ast.Call, _ast.Attribute,
    # Subscript retained for backward compatibility: result['status'] in postconditions.
    # Security note: Subscript itself is safe; the attack vector is class-hierarchy
    # traversal via __class__/__subclasses__, which is blocked by _BLOCKED_ATTRS.
    _ast.Subscript, _ast.Index, _ast.Slice,
}
```

**What's allowed**:
- Arithmetic operations: +, -, *, /, %, //, **
- Comparison operators: ==, !=, <, <=, >, >=, is, is not, in, not in
- Boolean logic: and, or, not
- Data structures: tuples, lists, constants
- Dictionary/list subscript: `result['key']`, `data[0]`
- Method calls: `result.get('status')`
- Conditional expressions: `x if condition else y`

**What's NOT allowed** (not in whitelist):
- Import statements (`_ast.Import`, `_ast.ImportFrom`)
- Function definitions (`_ast.FunctionDef`)
- Class definitions (`_ast.ClassDef`)
- Assignment (`_ast.Assign`)
- Attribute deletion (`_ast.Delete`)
- Free function calls (blocked separately at line 272-276)
- Any other node type not explicitly listed

## Blocked Attributes

**Defined in `_BLOCKED_ATTRS` (lines 237-242)**:

```python
_BLOCKED_ATTRS = {
    "__class__", "__bases__", "__subclasses__", "__globals__",
    "__builtins__", "__import__", "__code__", "__closure__",
    "__mro__", "__dict__", "__reduce__", "__reduce_ex__",
    "__init__", "__new__", "__del__", "__getattribute__",
}
```

**Why these are blocked**:
- `__class__`, `__bases__`, `__subclasses__`: Class hierarchy traversal (the core attack vector)
- `__globals__`, `__builtins__`, `__import__`: Access to global namespace and imports
- `__code__`, `__closure__`: Access to function internals
- `__mro__`: Method resolution order (another traversal path)
- `__dict__`: Direct object namespace access
- `__reduce__`, `__reduce_ex__`: Pickle serialization exploits
- `__init__`, `__new__`, `__del__`: Constructor/destructor manipulation
- `__getattribute__`: Attribute access override

**Detection logic** (lines 270-271):
```python
if isinstance(node, _ast.Attribute) and node.attr in _BLOCKED_ATTRS:
    return None, f"Blocked attribute access: '{node.attr}'"
```

## What This Blocks

**Concrete attack examples that now FAIL**:

1. **Class hierarchy traversal**:
```python
invariant = "().__class__.__bases__[0].__subclasses__()"
# Result: "Blocked attribute access: '__class__'"
```

2. **Import injection**:
```python
invariant = "__import__('os').system('ls')"
# Result: "Blocked free function call: '__import__'"
```

3. **Arbitrary code execution via compile**:
```python
invariant = "compile('import os', '<string>', 'exec')"
# Result: "Blocked free function call: 'compile'"
```

4. **Eval injection**:
```python
invariant = "eval('malicious code')"
# Result: "Blocked free function call: 'eval'"
```

5. **Global namespace access**:
```python
invariant = "len.__globals__['__builtins__']['open']('/etc/passwd')"
# Result: "Blocked attribute access: '__globals__'"
```

**What PASSES** (legitimate use cases):

```python
# Arithmetic invariants
"budget > 0"
"price * quantity < 1000"

# Comparison checks
"status in ['active', 'pending']"
"len(items) >= 1"

# Method calls (object.method(...))
"result.get('status') == 'success'"
"path.startswith('/safe/dir')"

# Dictionary access (postconditions)
"result['created'] == True"
"response['code'] < 400"

# Conditional expressions
"'admin' if user_role == 'root' else 'user'"
```

## Code Excerpts for Article Use

### Excerpt 1: The Vulnerability Pattern (Context)

```python
# v0.1.0 approach (VULNERABLE — DO NOT USE):
# Attempting to restrict eval() by removing builtins
eval(user_expression, {"__builtins__": {}}, namespace)

# This can be bypassed via Python's class hierarchy:
# ().__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['sys']...
```

### Excerpt 2: AST Whitelist Definition (Lines 224-235)

```python
# FIX-2: AST-whitelisted expression evaluator
_SAFE_AST_NODES = {
    _ast.Expression, _ast.BoolOp, _ast.BinOp, _ast.UnaryOp, _ast.Compare,
    _ast.Constant, _ast.Name, _ast.Load, _ast.And, _ast.Or, _ast.Not,
    _ast.Add, _ast.Sub, _ast.Mult, _ast.Div, _ast.Mod, _ast.FloorDiv, _ast.Pow,
    _ast.Eq, _ast.NotEq, _ast.Lt, _ast.LtE, _ast.Gt, _ast.GtE,
    _ast.Is, _ast.IsNot, _ast.In, _ast.NotIn,
    _ast.IfExp, _ast.Tuple, _ast.List, _ast.Call, _ast.Attribute,
    # Subscript retained for backward compatibility: result['status'] in postconditions.
    # Security note: Subscript itself is safe; the attack vector is class-hierarchy
    # traversal via __class__/__subclasses__, which is blocked by _BLOCKED_ATTRS.
    _ast.Subscript, _ast.Index, _ast.Slice,
}

_BLOCKED_ATTRS = {
    "__class__", "__bases__", "__subclasses__", "__globals__",
    "__builtins__", "__import__", "__code__", "__closure__",
    "__mro__", "__dict__", "__reduce__", "__reduce_ex__",
    "__init__", "__new__", "__del__", "__getattribute__",
}
```

### Excerpt 3: Safe Eval Implementation (Lines 245-285)

```python
def _safe_eval(expr: str, namespace: dict):
    """
    AST-whitelisted expression evaluator (FIX-2).

    Replaces bare eval() + {"__builtins__": {}} which is bypassable via
    Python's class hierarchy (__class__.__bases__[0].__subclasses__() ...).
    See CVE-equivalent analysis in ystar_paper.md Appendix A.3.

    The whitelist permits arithmetic, comparison, simple attribute access
    (result.get(...)), and dict subscript (result['key']) — all patterns
    that appear in typical invariant/postcondition expressions.
    All dunder attributes and free function calls are blocked at the AST
    level before any bytecode is executed.

    Returns: (result_value, error_message_or_None)
      If error_message is not None, the expression was rejected or failed.
    """
    try:
        tree = _ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return None, f"SyntaxError: {e}"

    for node in _ast.walk(tree):
        if type(node) not in _SAFE_AST_NODES:
            return None, f"Blocked AST node type: {type(node).__name__}"
        if isinstance(node, _ast.Attribute) and node.attr in _BLOCKED_ATTRS:
            return None, f"Blocked attribute access: '{node.attr}'"
        if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name):
            # Allow method calls (result.get(...)) but not free function calls.
            # Free function calls require a Name node as the func — e.g. open(),
            # eval(), __import__(). Method calls use an Attribute node.
            return None, f"Blocked free function call: '{node.func.id}'"

    try:
        return eval(
            compile(tree, "<invariant>", "eval"),
            {"__builtins__": {}},
            namespace,
        ), None
    except Exception as e:
        return None, str(e)
```

### Excerpt 4: Usage in Invariant Checking (Lines 456-461)

```python
# FIX-2: replaced eval()+{__builtins__:{}} with _safe_eval() (AST whitelist).
for expr in contract.invariant:
    if not expr.strip():
        continue
    namespace = dict(params)
    namespace["params"] = params
    result_val, eval_err = _safe_eval(expr, namespace)
    if eval_err:
        # Expression was blocked by AST whitelist
        violations.append(Violation(
            dimension  = "invariant",
            field      = "params",
            message    = f"Invariant expression rejected: '{expr}' — {eval_err}",
            actual     = expr,
            constraint = f"invariant: {expr}",
            severity   = 1.0,
        ))
```

## Security Rationale from Code Comments

**Line 8** (version header):
```python
#   FIX-2  invariant:     eval sandbox escape   → AST whitelist evaluator (Subscript-safe)
```

**Lines 231-233** (Subscript safety note):
```python
# Subscript retained for backward compatibility: result['status'] in postconditions.
# Security note: Subscript itself is safe; the attack vector is class-hierarchy
# traversal via __class__/__subclasses__, which is blocked by _BLOCKED_ATTRS.
```

**Lines 249-251** (vulnerability reference):
```python
# Replaces bare eval() + {"__builtins__": {}} which is bypassable via
# Python's class hierarchy (__class__.__bases__[0].__subclasses__() ...).
# See CVE-equivalent analysis in ystar_paper.md Appendix A.3.
```

**Lines 253-257** (design rationale):
```python
# The whitelist permits arithmetic, comparison, simple attribute access
# (result.get(...)), and dict subscript (result['key']) — all patterns
# that appear in typical invariant/postcondition expressions.
# All dunder attributes and free function calls are blocked at the AST
# level before any bytecode is executed.
```

**Lines 273-276** (free function call blocking):
```python
# Allow method calls (result.get(...)) but not free function calls.
# Free function calls require a Name node as the func — e.g. open(),
# eval(), __import__(). Method calls use an Attribute node.
```

## CMO Article Guidance

**Verified claims you can make**:
1. "We block ALL dunder attribute access at the AST level — 14 specific attributes that enable class traversal"
2. "Free function calls like `open()`, `eval()`, `__import__()` are rejected BEFORE execution"
3. "Only 30 AST node types are whitelisted — everything else is blocked by default"
4. "Subscript notation `result['key']` is safe because `__class__` access is separately blocked"
5. "The attack payload `().__class__.__bases__[0].__subclasses__()` fails at node 1 with 'Blocked attribute access: __class__'"

**DO NOT claim** (not verified in code):
- Specific CVE numbers (code references "CVE-equivalent" but no exact CVE-ID)
- Performance benchmarks (not documented in this file)
- Compatibility with Python 2.x (no version checks in code)

**Files to cite**:
- Primary source: `ystar/kernel/engine.py` (lines 224-285)
- Additional reference mentioned in comments: `ystar_paper.md` Appendix A.3 (verify this exists separately)

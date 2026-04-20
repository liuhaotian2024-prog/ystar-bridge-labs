# CZL-WHITEBOARD-BROKER-SUB-SAMEFIX Receipt

## Y* (verifiable predicate)
Wipe vulnerability (truncate-before-lock race) closed across all 3 board writers: dispatch_board.py, cto_dispatch_broker.py, engineer_task_subscriber.py.

## Xt (current state before fix)
- cto_dispatch_broker.py had its own local _read_board() / _write_board() copies with the same 3 bugs from WIPE-RCA
- engineer_task_subscriber.py delegates to dispatch_board.py claim via subprocess -- already safe
- Broker had 6+ read-modify-write call sites all using the unsafe pattern

## U (actions taken)

### Edit 1: scripts/cto_dispatch_broker.py
Replaced local vulnerable _read_board() / _write_board() with imports from dispatch_board.py.
Converted 4 functions to locked critical sections: poll_and_route, validate_completed_tasks, _auto_post_task, verify_task.
Created _next_czl_id_locked(board) to avoid nested lock deadlock.

### Edit 2: engineer_task_subscriber.py -- NO CHANGE NEEDED
Subscriber uses subprocess.run to call dispatch_board.py claim -- already uses the fixed code path.

### Extended concurrent regression tests
Added 3 new tests: broker_post_concurrent, broker_subscriber_concurrent, concurrent_reads_during_broker_writes.
12 passed in 2.84s

## Yt+1
All board access shares governance/.dispatch_board.lock. 12/12 tests pass.

## Rt+1
0

## Files Modified
- scripts/cto_dispatch_broker.py
- tests/platform/test_dispatch_board_concurrent.py
- reports/receipts/CZL-WHITEBOARD-BROKER-SUB-SAMEFIX.md

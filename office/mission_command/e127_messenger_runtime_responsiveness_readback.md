# E127 Aiden Messenger Runtime Responsiveness Readback

E127 fixes the failure mode where the meeting room appears frozen after the owner sends a memo or question.

The root cause was not owner misuse. The browser submitted the message and then waited silently while the local server synchronously ran the full Aiden runtime. If that runtime was slow, blocked, or threw an exception, the page did not show a pending message, progress, timeout, or correct-path notice.

What changed:

- The local server now uses a threaded HTTP server.
- Runtime calls are wrapped by a watchdog timeout.
- Timeout and exception paths return a governed Aiden runtime notice instead of silently hanging.
- The browser immediately shows the owner's pending message.
- The browser shows an Aiden runtime status line while the governed retrieval/brain/CIEU path is running.
- The browser has its own timeout and displays a visible notice if the server does not return.
- The send box disables during a pending turn to avoid duplicate stuck submissions.

Truth boundary:

- No external send occurred.
- No provider action executed.
- No payment executed.
- The change is local-only and only improves runtime visibility/recoverability.

Remaining limitation:

The timeout notice does not make the heavy Aiden path faster. It makes failure visible. The next improvement should split lightweight chat/memo turns from heavyweight strategic runtime cycles so Aiden can respond quickly when the owner is just leaving a memo.

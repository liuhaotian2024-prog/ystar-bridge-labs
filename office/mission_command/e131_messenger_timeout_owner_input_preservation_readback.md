# E131 Messenger Timeout Owner Input Preservation

E131 fixes the unacceptable behavior where the owner message disappeared after a runtime timeout.

The server timeout/error path now returns two visible messages:

- the preserved owner input,
- then the Aiden runtime notice.

The browser also has a fallback preservation path if the server or browser request fails before a structured payload arrives.

Timeouts were adjusted for live public-read:

- server watchdog default: 120 seconds,
- browser request timeout: 150 seconds.

No external action, provider execution, payment, customer validation, revenue signal, or K9Audit write occurred.

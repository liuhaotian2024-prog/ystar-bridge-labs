# E129 Strategy Runtime Receipt Chinese Rendering

E129 fixes the case where Aiden returned an English strategy runtime receipt directly to the owner.

The messenger now detects E114/E108-style strategy runtime receipts and renders them as a Chinese explanation:

- What actually ran.
- What strategy path was selected.
- Why the machine selected it.
- Which alternative routes were considered.
- What the result does and does not prove.
- What boundaries remain.

The raw machine receipt is still preserved inside the runtime artifact for audit/debug. The visible owner-facing reply is no longer a raw log dump.

The UI also wraps long route ids and technical fields so they do not overflow message boundaries.

No external action, customer validation, revenue signal, payment, provider execution, or K9Audit write occurred.

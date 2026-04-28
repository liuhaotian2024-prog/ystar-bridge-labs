# Field Projection Algorithm v0

For each layer transition:
1. inherit parent Y* obligations
2. identify layer-specific context
3. contract or narrow obligations based on current context
4. bind concrete constraints
5. preserve forbidden boundaries
6. emit unresolved gaps instead of guessing
7. produce child Y*
8. record trace refs and evidence refs

This algorithm makes no mathematical optimality claim, uses no probabilistic scoring, and performs no semantic truth scoring.

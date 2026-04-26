# CIEU Feedback Contract

This contract describes how a future Pre-U packet should connect to CIEU. It
does not claim that this event wiring exists today.

Future CIEU behavior:

- A pre-action CIEU event should reference `packet_id`.
- A post-action CIEU event should record actual `Yt+1` and actual `Rt+1`.
- CIEU should compare `predicted_y_t1` against actual `Yt+1`.
- CIEU should compare `predicted_r_t1` against actual `Rt+1`.
- The prediction delta should become brain nutrition.
- If the selected action fails to reduce residual, CIEU should mark a learning signal.
- If a non-selected candidate would likely have been better, CIEU should mark a counterfactual learning candidate.

Minimum future event relationship:

```text
pre_action_packet(packet_id)
  -> action_attempt
  -> post_action_outcome
  -> predicted_vs_actual_delta
  -> brain_nutrition_candidate
```

The packet should not be treated as evidence of what happened. It is evidence of
what Aiden predicted before acting. Actual outcome evidence belongs to CIEU after
the action.

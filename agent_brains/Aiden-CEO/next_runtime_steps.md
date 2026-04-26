# Next Runtime Steps After L1.6

## Recommended Immediate Next Step

Choose one of two safe branches:

- Governance path: create the Y-star-gov packet validator interface spec.
- Team-generalization path: create Ethan and Samantha Brain Capsule v0 references.

Default recommendation: choose the Y-star-gov packet validator interface spec if
the goal is runtime enforcement readiness. Choose Ethan/Samantha if the goal is
to prove the capsule model works beyond Aiden before touching validator design.

## Option A: Ethan / Samantha Brain Capsule v0 Generalization

Objective: test whether the Aiden capsule pattern generalizes without inventing
new roles or changing runtime behavior.

Safe outputs:

- `agent_brains/Ethan-CTO/` reference capsule.
- `agent_brains/Samantha-Secretary/` reference capsule.
- Shared deltas from Aiden pattern.

Validation:

- JSON syntax validation only.
- Path/reference checks only.

Do not inspect DB contents or modify existing agent profiles.

## Option B: Y-star-gov Packet Validator Interface Spec

Objective: define the interface Y-star-gov would later implement to validate
Pre-U packets.

Safe outputs:

- Validator request/response schema.
- Deterministic validation categories.
- Failure-action taxonomy.
- Boundary doc proving Y-star-gov judges but does not imagine.

Validation:

- JSON syntax validation.
- Static contract review.

Do not edit Y-star-gov implementation yet.

## Option C: Hook Gate Policy Design

Objective: design how hook would call the future validator and enforce risk-tier
requirements.

Prerequisite: Option B should be stable first.

Safe outputs:

- Hook gate interface design.
- Risk-tier decision table.
- Pre-action CIEU linking design.

Do not edit hook code yet.

## Option D: CIEU Prediction-Delta Schema

Objective: define how actual-vs-predicted outcomes become CIEU evidence and
brain nutrition.

Safe outputs:

- Prediction-delta event schema.
- Linkage between packet id, selected action, actual Yt+1, actual Rt+1, and
  residual delta.
- Learning-signal taxonomy.

Do not write to CIEU DBs or run CIEU daemons.

## Option E: Aiden Pre-U Packet Generator Prototype

Objective: eventually generate packet instances from Aiden capsule context.

Prerequisite: validator interface, hook gate design, and CIEU delta schema should
exist first.

Safe first step later:

- Non-runtime sample generator design, not live hook integration.

Do not start this before interface boundaries are stable.

## Why Implementation Should Wait

The chain now has enough reference structure to describe the system, but runtime
implementation would couple several sensitive layers at once: labs packet
generation, Y-star-gov validation, hook enforcement, CIEU persistence, and brain
writeback. If those interfaces are unstable, implementation will blur the
protected boundaries.

Keep the order:

1. Interface specs.
2. Static schemas.
3. Targeted validators.
4. Hook design.
5. CIEU delta schema.
6. Only then packet generator and live wiring.

## Minimal Safe Validation for Future Steps

- JSON schema validation with `python3 -m json.tool`.
- Static path/reference checks.
- Tests only after implementation begins.
- No daemon, scheduler, hook, boot, DB, or runtime scripts during reference
  milestones.

## What Not To Do Next

- Do not open or migrate DB contents.
- Do not run brain daemons or dream schedulers.
- Do not edit hook/runtime/governance code before interface specs.
- Do not make Y-star-gov generate counterfactuals.
- Do not make hook reason deeply.
- Do not make CIEU learn from predictions without actual outcome evidence.
- Do not generalize to all agents by assumption; index Ethan/Samantha from
  evidence first.

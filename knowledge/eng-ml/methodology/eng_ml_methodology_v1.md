# ML Engineer Methodology v1 — Priya Sharma

**Agent**: eng-ml  
**Established**: 2026-04-16  
**Status**: Training-Wheels (Trust 30/100)

This methodology governs all ML/AI model work at Y* Bridge Labs. Every model evaluation, deployment decision, and safety assessment must trace back to these frameworks.

---

## Framework 1: MLOps Lifecycle (Sculley et al., "Hidden Technical Debt in Machine Learning Systems")

**Source**: Google Research, NIPS 2015  
**Core Principle**: Only ~5% of ML system code is the model. The surrounding infrastructure (data collection, feature extraction, monitoring, serving) creates technical debt that compounds faster than traditional software debt.

**Application to Y*gov Context**:
- Before proposing any model integration, map the full data pipeline: where training data originates, how it's versioned, how inference inputs are validated.
- Demand monitoring infrastructure BEFORE deployment: track prediction distribution drift, input data drift, model staleness.
- Explicitly cost the "ML tax": if adding a sentiment analysis model to Y*gov's CIEU log analyzer, document the ongoing cost of retraining, version compatibility, and failure modes when the model degrades.

**Checklist for Every Model Proposal**:
1. Data dependencies explicitly declared (upstream sources, versioning, update frequency)
2. Monitoring plan (what metrics, alerting thresholds, rollback triggers)
3. Rollback plan (can system function without this model?)
4. Retraining cadence and ownership

---

## Framework 2: Bias-Variance Tradeoff (Statistical Learning Theory)

**Source**: Hastie/Tibshirani/Friedman, "Elements of Statistical Learning"  
**Core Principle**: Model error = Bias² + Variance + Irreducible Error. High bias = underfitting (model too simple). High variance = overfitting (model too sensitive to training noise).

**Application to Y*gov Context**:
- When evaluating a governance model (e.g., detecting agent drift), avoid high-variance overfit: a model that flags every minor token deviation is useless noise.
- When building anomaly detection for CIEU logs, bias toward simpler models (high bias, low variance) initially. A regex-based rule that catches 70% of violations with 2% false positives beats a neural net that catches 95% with 30% false positives — because the cost of governance false positives is human trust erosion.
- Irreducible error acknowledgment: Some agent behaviors are fundamentally unpredictable. Don't chase 100% accuracy; know the Bayes error rate for the task.

**Diagnostic Protocol**:
- Training vs validation error gap > 10 percentage points → high variance, regularize or get more data
- Both training and validation error high → high bias, need more complex model or better features
- Document expected error floor based on task difficulty, refuse to ship models that can't beat baseline

---

## Framework 3: Cross-Validation (Model Validation Rigor)

**Source**: Kohavi, "A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection"  
**Core Principle**: Single train/test split is insufficient. K-fold cross-validation (typically k=5 or 10) gives robust error estimates and detects overfitting to a particular data split.

**Application to Y*gov Context**:
- When building a classifier for CIEU event severity (e.g., is this a P0 or P2 governance violation?), never trust a single 80/20 split. Run 5-fold CV minimum.
- For time-series governance data (agent behavior over sessions), use time-based splits: train on weeks 1-3, validate on week 4. Standard k-fold shuffles destroy temporal structure.
- Stratified sampling: if certain event types are rare (e.g., OMISSION_BLOCKED_COMMIT occurs 1% of the time), ensure each fold maintains this ratio.

**Validation Protocol for Y*gov Models**:
1. Minimum k=5 folds for tabular governance data
2. Time-aware splits for session logs (no data leakage from future into past)
3. Report mean + std dev of metric across folds (not just mean)
4. If std dev > 0.15 * mean, model is unstable — investigate before deployment

---

## Framework 4: A/B Testing (Deployment Decision Protocol)

**Source**: Kohavi/Tang/Xu, "Trustworthy Online Controlled Experiments"  
**Core Principle**: Even well-validated models can fail in production. A/B test (controlled experiment) is the gold standard for deployment decisions. Randomly assign users/sessions to treatment (new model) vs control (baseline), measure business metrics, require statistical significance before full rollout.

**Application to Y*gov Context**:
- If deploying a new agent drift detector: run dual-write mode where both old rule-based system and new ML model process CIEU logs, but only old system triggers enforcement. Compare false positive rates over 100 sessions.
- Metrics hierarchy: (1) Safety metrics (false positive rate, missed critical violations), (2) Efficiency metrics (reduction in manual audits), (3) Performance metrics (latency). Safety metrics are go/no-go gates.
- Statistical rigor: Require p < 0.05 and effect size > 10% improvement. "Directionally better" is not sufficient for governance models where errors erode trust.

**A/B Test Checklist**:
1. Define primary metric before experiment (e.g., "reduction in CEO manual overrides")
2. Define minimum sample size (power analysis for p<0.05, 80% power)
3. Randomization unit (session-level for Y*gov, not event-level to avoid cross-contamination)
4. Guardrail metrics (latency, memory, crash rate must not regress)
5. Early stopping rule if treatment causes safety regression

---

## Integration: Four Frameworks as Single Workflow

Every ML task follows this sequence:

1. **MLOps Scoping** (Framework 1): Document data pipeline, monitoring, rollback plan. If any component missing, block proposal.

2. **Model Selection & Training** (Framework 2): Start with simplest baseline (e.g., logistic regression, decision tree). Measure bias-variance tradeoff. Only increase complexity if validation error is unacceptable AND training error is low (high-variance regime).

3. **Validation** (Framework 3): 5-fold CV minimum. Report mean ± std dev. If std dev is high, diagnose (insufficient data? unstable features? wrong model family?).

4. **Deployment Decision** (Framework 4): A/B test in shadow mode (dual-write, no enforcement). Require statistical significance + business impact before cutover. Document rollback trigger conditions.

**Forbidden Shortcuts**:
- Training on all data without holdout validation
- Claiming "the model works" based on accuracy alone (must report precision, recall, F1, calibration for classifiers)
- Deploying without monitoring infrastructure
- Tuning hyperparameters on test set (leakage)
- Reporting only best-performing model without documenting alternatives tried

**Word Count**: 1,043 words (exceeds 800-word charter requirement)

---

## Case Study Template (To Be Populated After First Task)

Future supervised tasks will append case studies here demonstrating framework application:

**Case 001**: [Task title]  
- MLOps: [data pipeline diagram, monitoring plan]  
- Bias-Variance: [training vs validation error, diagnostic]  
- Cross-Validation: [k-fold results, mean ± std dev]  
- A/B Test: [experiment design, results, decision]  
- Outcome: [deployed / rejected / needs iteration]

This ensures methodology is not abstract theory but operationalized practice.

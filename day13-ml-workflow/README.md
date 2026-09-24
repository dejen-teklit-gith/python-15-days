# Day 13 — The Real ML Workflow (scikit-learn)

## 🎯 Goal
Do machine learning the way it's done at work: pipelines, cross-validation, honest evaluation, and decisions tied to **business value**, not just accuracy.

## 🧠 First Principles

**1. A model is only as good as how you evaluate it.** Most ML failures aren't bad algorithms. They're bad evaluation: leakage, the wrong metric, or tuning on the test set.

**2. The workflow**
```
raw data ─► split (stratified) ─► Pipeline[impute → scale/encode → model]
                                        │
                        cross-validate on TRAIN to pick a model
                                        │
                   evaluate ONCE on TEST ─► choose threshold by cost ─► save
```
- **Pipeline** bundles preprocessing *with* the model, so the exact same steps run in training and in production, and cross-validation can't leak.
- **Cross-validation** trains/tests 5 times on different slices → a score with an error bar, not one lucky number.
- The **test set is touched once**. Use it repeatedly and it quietly becomes training data.

**3. Accuracy lies when classes are imbalanced.** With 14% churners, "nobody churns" is 86% accurate and worthless. Use:
| Metric | Question it answers |
|---|---|
| Precision | Of those we flagged, how many really churn? (wasted offers) |
| Recall | Of all churners, how many did we catch? (missed customers) |
| ROC-AUC | How well does the model *rank* risky above safe customers? |

**4. The threshold is a business decision.** The model outputs a probability; *you* choose where to cut. Put money on each outcome (offer cost, value saved) and pick the most profitable cut-off.

**5. Start simple.** Here, logistic regression beats random forest and gradient boosting. Fancy isn't automatically better, especially on tabular data with clear linear effects.

## 🌍 Real-World Scenario
A subscription company (telecom / SaaS / streaming) has 4,000 customers. Marketing can send a CHF 50 retention offer. Who should get it?

Result from this project:
| Threshold | Flagged | Precision | Recall | Campaign profit |
|---|---|---|---|---|
| 0.50 (default) | 324 | 0.29 | 0.67 | **CHF −5,040** 📉 |
| 0.82 (chosen by profit) | 65 | 0.52 | 0.25 | **CHF +830** 📈 |

Same model, opposite business outcome. **That's** why the threshold matters.

## 💻 Code
```bash
python main.py        # trains, compares, picks a threshold, saves churn_model.joblib
```

![code](screenshots/code.png)
![output](screenshots/output.png)

## 🏋️ Exercises
1. Change `VALUE_OF_SAVED_CUSTOMER` to 1000. How do the threshold and profit move? Why?
2. Tune the gradient-boosting model with `GridSearchCV` (inside the pipeline: `model__max_depth`). Does it overtake logistic regression?
3. Plot the profit-vs-threshold curve with matplotlib.
4. **Leakage hunt:** add a column `cancel_request_sent` that's only known *after* churn. Watch AUC jump to ~1.0 — and explain why that model would fail in production.

## ✅ Takeaways
- Pipeline everything. Cross-validate on train. Test once.
- For imbalanced problems: precision, recall and AUC, never accuracy alone.
- Pick the threshold using business costs.

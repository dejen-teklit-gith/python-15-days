# Day 15 — Capstone: Ship It 🚀

## 🎯 Goal
Take the churn model from Day 13 and turn it into a **production-style service**: an API with a contract, tests, logging, a quality gate and a Docker image anyone can run with one command.

## 🧠 First Principles

**1. Software isn't done until someone else can run it.** A notebook that works on your laptop is a prototype. A service is: *clone → one command → it works*, and it keeps working when the inputs are weird.

**2. Train and serve are two different programs.**
```
train.py ──► model/churn_model.joblib (pipeline + metadata) ──► app/main.py (loads once, serves many)
```
Load the model **once at startup**, never per request. Save **metadata** with it (version, AUC, threshold) so you always know what's running.

**3. The API schema is a contract.** `Literal["monthly", "one_year", "two_year"]` means a typo like `"weekly"` gets a clear `422` instead of a silent wrong prediction.

**4. Quality gates stop bad models from shipping.** `train.py` refuses to save a model below AUC 0.75, the same way tests stop broken code.

**5. Containers make "works on my machine" true everywhere.** A Docker image freezes the OS, Python version, libraries, code *and* model into one artifact.

## 🧩 How every day shows up here
| Day | Where it appears |
|---|---|
| 1–3 | types, functions, dicts/lists throughout |
| 4 | validation at the boundary (Pydantic), error handling |
| 5 | `BaseModel` classes as data contracts |
| 6 | decorators (`@app.post`), context managers (`lifespan`) |
| 7 | tests, logging, project structure |
| 8 | async middleware / ASGI server |
| 9–10 | HTTP API with FastAPI |
| 11 | pandas for model input |
| 12–13 | the trained ML pipeline + business threshold |

## 🌍 Real-World Scenario
The CRM team wants to call an endpoint every night with all active customers and get back **who should receive a retention offer**. The data science team (you) must deliver a service, not a notebook.

## 💻 Run it
```bash
# Option A — local
pip install -r requirements.txt
python train.py                         # trains + saves model/churn_model.joblib
uvicorn app.main:app --reload           # open http://127.0.0.1:8000/docs
pytest -v                               # 9 end-to-end tests

# Option B — Docker (no Python needed on the machine)
docker build -t churn-api .
docker run -p 8000:8000 churn-api
```
```bash
curl -X POST localhost:8000/predict -H "content-type: application/json" -d '{
  "tenure_months": 3, "contract": "monthly", "plan": "basic", "monthly_fee": 110,
  "support_tickets_90d": 5, "autopay": false, "logins_30d": 1}'
# → {"churn_probability":0.99,"risk":"high","send_retention_offer":true,"model_version":"..."}
```

![swagger](screenshots/docs.png)
![tests](screenshots/tests.png)
![docker](screenshots/docker.png)

## 🏋️ Stretch goals
1. Deploy the container for free on **Render**, **Fly.io** or **Google Cloud Run**, and put the live `/docs` URL at the top of this README.
2. Add an `X-API-Key` header check (key from an environment variable).
3. Log every prediction to SQLite (Day 10) and add `/stats` with the daily share of high-risk customers. That's the start of **model monitoring**.
4. Add a GitHub Actions workflow that runs `pytest` and `docker build` on every push.

## 🧭 What next? (turning 15 days into mastery)
Pick **one** track and build 3 projects in it over the next month:
| Track | Build next |
|---|---|
| **Backend** | Auth (JWT), PostgreSQL + SQLAlchemy, background jobs (Celery/RQ), Redis cache |
| **Data** | Airflow/Prefect pipeline, dbt, a Streamlit dashboard on real open data |
| **ML** | Kaggle competition end-to-end, MLflow experiment tracking, model monitoring |
| **AI / LLM** | RAG with neural embeddings + a vector DB, tool-using agents, evaluation sets |
| **Automation** | Playwright web automation, scheduled reports, Slack/Teams bots |

## ✅ Takeaways
- Train → save with metadata → load once → serve with a strict schema.
- Tests + quality gate + container = something a team can trust.
- You now know how every layer of a real Python AI product fits together. 🎓

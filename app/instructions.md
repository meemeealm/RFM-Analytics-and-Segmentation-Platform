# Project Instructions

## Role
You are working on a FastAPI ML inference system called Customer Lifecycle Intelligence Orchestrator.

---

## Architecture Rules
- Use FastAPI
- Use service layer (routes → services → ml layer)
- Keep routes thin
- Business logic goes in services/
- ML logic goes in ml/


---

## ML Rules
- Model is already trained (KMeans)
- DO NOT retrain model
- Cache model in memory (app.state or singleton)

---

## API Rules
- Base path: /api/v1
- Must include:
  - /customers/predict
  - /customers/predict/batch
  - /clusters
  - /health

---

## Data Rules
- RFM inputs only:
  - recency >= 0
  - frequency >= 0
  - monetary >= 0

---

## Output Rules
- Always return business-friendly responses
- Never expose raw model internals
- Always map cluster → business meaning

---

## Coding Style
- Type hints required
- Pydantic v2 schemas
- Async endpoints preferred
- No monolithic route files

---

## Security
- Add API key placeholder
- Add CORS middleware

---

## Dependency Management
- Use uv
- No pip commands
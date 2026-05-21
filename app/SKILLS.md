# Customer Intelligence Orchestrator — Skills Definition

This document defines all available skills (API tools) used by the Customer Intelligence Orchestrator system.

All skills are inference-only. No training or data mutation operations are allowed.

---

# Global Rules

- Never return raw database IDs or internal system identifiers.
- Never expose model internals (weights, scaler values, centroids).
- Always return business-readable outputs.
- All numeric inputs must be validated (>= 0 where applicable).
- All outputs must include business interpretation, not just raw predictions.
- Skills are stateless.

---

# 1. Skill: Predict Customer Segment

## Name
`predict_customer_segment`

## Description
Predicts the customer cluster using pre-trained KMeans model based on RFM features.

## Input Schema

```json
{
  "customer_id": "string (optional)",
  "recency": "float",
  "frequency": "float",
  "monetary": "float"
}
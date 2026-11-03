# MedServicePrice.kz — Sprint 2 (Team 12)

This repository contains the code developed in Sprint 2 (29 Oct – 4 Nov 2026) of MedServicePrice.kz, a price aggregator for medical services in Kazakhstan.

**Sprint Goal:** "Patients can narrow price results with filters and see clinics on a map, and the team can moderate unmatched service names (with AI suggestions) so more real prices reach search."

## User stories and files

| User story | Files |
|---|---|
| US3 — Filters and sorting | `backend/app/services/queries.py`, `backend/app/services/search.py`, `backend/app/core/redis_client.py`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts`, `frontend/src/hooks/queries.ts`, `frontend/src/pages/SearchResultsPage.tsx` |
| US5 — Moderation of unmatched names, AI catalogue suggestions | `backend/app/services/normalization.py`, `backend/app/api/admin.py`, `backend/app/services/ai_normalize.py`, `backend/app/tasks/normalize_ai_task.py`, `backend/alembic/versions/0006_catalog_suggestions.py`, `backend/tests/test_normalization.py`, `backend/run_tests.py`, `backend/conftest.py`, `backend/pytest.ini`, `frontend/src/components/admin/widgets.tsx`, `frontend/src/pages/admin/AdminNormalization.tsx` |
| US7 — Clinic map | `backend/app/api/public.py`, `backend/app/schemas/responses.py`, `backend/app/services/geocode.py`, `backend/app/tasks/geocode_task.py`, `frontend/src/components/MapView.tsx`, `frontend/src/pages/MapPage.tsx` |

## Note

This is an extract of the full application (FastAPI + PostgreSQL + Celery backend, React + TypeScript frontend). These files rely on the rest of that codebase (models, config, database) to run.

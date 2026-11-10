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

## Sprint 3 (SIS 10–11): improvements and Change Request CR-01

| ID | Change | Files |
|---|---|---|
| ISS-01 | The price-drop subscription form on the service page never called the API. Fixed: the form now calls `POST /api/subscriptions` with loading and error states; the endpoint validates that the service/clinic exist (404 otherwise) and is idempotent (`already_subscribed` instead of a duplicate row). | `backend/app/api/public.py`, `backend/app/schemas/responses.py`, `frontend/src/pages/ServiceDetailPage.tsx`, `frontend/src/api/client.ts` |
| ISS-02 | An inverted price range (`price_min > price_max`) returned an empty result that looked like "no clinics". Fixed: `GET /api/offers` returns 422, and the search page explains the problem and offers "Swap values". | `backend/app/api/public.py`, `frontend/src/pages/SearchResultsPage.tsx` |
| ISS-03 | After resolving an unmatched name in moderation, results appeared only after the cache TTL expired. Fixed: the cache is cleared after resolve. | `backend/app/api/admin.py` |
| CR-01 | Clinic price benchmark: each clinic price compared with the same service in its city (min / median / max, rank, position). API: `GET /api/clinics/{id}/benchmark` and `GET /api/clinics/{id}/benchmark.csv`; UI: "Price benchmark" section on the clinic profile; 9 unit tests. | `backend/app/services/benchmark.py`, `backend/app/api/public.py`, `backend/app/schemas/responses.py`, `backend/app/schemas/__init__.py`, `backend/tests/test_benchmark.py`, `frontend/src/api/types.ts`, `frontend/src/api/client.ts`, `frontend/src/hooks/queries.ts`, `frontend/src/components/PriceBenchmark.tsx`, `frontend/src/pages/ClinicProfilePage.tsx` |

RU/KZ translations for these changes: `frontend/src/lib/i18n-dict.ts`.

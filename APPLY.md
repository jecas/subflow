# Applying this upgrade

This ZIP contains the files that are new or changed relative to the `feature/bootstrap` branch inspected on 2026-09-22.

Copy each file to the same path in the repository. Existing files with the same path should be replaced.

New directories:
- `app/providers/`

New migration:
- `alembic/versions/0002_payments_and_webhooks.py`

After applying, run GitHub Actions. Recommended follow-up before merging:
1. `ruff check .`
2. Alembic upgrade/downgrade/upgrade
3. unit tests
4. integration tests
5. Docker build

Note: the package deliberately does not modify `0001_initial_schema.py`; schema evolution is represented by migration `0002`.

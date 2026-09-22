## Plan: Add FastAPI Backend Tests

Add a root-level pytest suite using FastAPI's `TestClient`. Cover every current route branch while isolating the module-level `activities` dictionary with a per-test cloned store, so signup and unregister tests remain deterministic and cannot affect one another. Keep the change test-only: no application, dependency, configuration, or documentation edits.

**Steps**
1. Create `/workspaces/skills-getting-started-with-github-copilot/tests/test_app.py` and import the application module plus `TestClient`, `pytest`, and `deepcopy`.
2. Add a pytest client fixture that uses `monkeypatch` to replace `src.app.activities` with a deep copy for each test, then yields a `TestClient` for `src.app.app`. This preserves nested participant-list isolation and lets pytest restore the original module global after each test.
3. Test `root` with redirect following disabled, asserting the current `307` response and `/static/index.html` location.
4. Test `get_activities`, asserting `200` and that the JSON payload matches the isolated activity store, including the expected activity records and participant data.
5. Test `signup_for_activity` across all current branches: successful signup returns the exact message and persists in a subsequent activities response; duplicate signup returns `400` with the documented detail and does not duplicate the participant; unknown activity returns `404`; omitted `email` returns FastAPI's `422` validation response.
6. Test `unregister_from_activity` across all current branches: successful unregister returns the exact message and removal is visible in a subsequent activities response; unenrolled student returns `404` without changing participants; unknown activity returns `404`; omitted `email` returns `422`.
7. Keep assertions scoped to current contracts. Do not add expectations for unenforced behavior such as maximum-capacity rejection or email-format validation.

**Relevant files**
- `/workspaces/skills-getting-started-with-github-copilot/tests/test_app.py` — new API tests and isolated `TestClient` fixture.
- `/workspaces/skills-getting-started-with-github-copilot/src/app.py` — read-only contract under test: `app`, `activities`, `root`, `get_activities`, `signup_for_activity`, and `unregister_from_activity`.
- `/workspaces/skills-getting-started-with-github-copilot/pytest.ini` — existing `pythonpath = .` supports importing `src.app`; no change needed.

**Verification**
1. Run `python -m pytest tests -q` from `/workspaces/skills-getting-started-with-github-copilot` and confirm all route and validation tests pass.
2. Run `python -m pytest -q` to confirm normal repository discovery also finds and passes the new suite.
3. Confirm mutation isolation by ensuring the original `src.app.activities` participant lists are unchanged after the suite, either through an explicit fixture-restoration assertion or by rerunning the suite and obtaining identical results.

**Decisions**
- Place tests in the separate root-level `/workspaces/skills-getting-started-with-github-copilot/tests/` directory.
- Cover all endpoint branches, including framework-generated missing-query validation.
- Use synchronous `TestClient`; the handlers are synchronous and `httpx` is already present.
- Tests only: deliberately exclude changes to `requirements.txt`, both README files, `pytest.ini`, and production code.
- Do not add `tests/__init__.py`; pytest discovery and the configured root import path do not require the tests directory to be a package.

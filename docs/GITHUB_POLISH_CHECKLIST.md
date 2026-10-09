# GitHub Polish Checklist

Use this checklist before sharing the repository with a client, reviewer, or employer.

## Repository Profile

- [ ] Add a short GitHub repository description.
- [ ] Add topics: `fastapi`, `nextjs`, `typescript`, `sqlalchemy`, `mssql`, `fleet-management`, `vehicle-rental`, `erp`.
- [ ] Pin the repository if it should appear on a profile.
- [ ] Confirm screenshots render correctly in the README.

## Documentation

- [ ] Keep `README.md` focused on what the project is and how to run it.
- [ ] Keep `docs/MVP_STATUS.md` honest and current.
- [ ] Keep `docs/API_MAP.md` aligned with actual routes.
- [ ] Keep screenshots updated when UI changes significantly.
- [ ] Add a short demo script if presenting the app live.

## Security And Secrets

- [ ] Confirm `.env`, `.env.local`, database backups, and secrets are not committed.
- [ ] Move database credentials out of source code before production use.
- [ ] Use HTTPS and secure cookies in deployed environments.
- [ ] Scrub screenshots and demo data for sensitive information.

## Engineering Quality

- [ ] Run backend tests before sharing.
- [ ] Run frontend lint/build before sharing.
- [ ] Avoid committing generated build output, virtual environments, or local caches.
- [ ] Keep `generated_models/models.py` read-only unless regenerated intentionally.
- [ ] Document any guarded or intentionally blocked workflow.

## Nice To Have

- [ ] Add a short demo video or GIF.
- [ ] Add a release note for the current MVP scope.
- [ ] Add a simple architecture diagram image.
- [ ] Add sample API requests for the most important workflows.

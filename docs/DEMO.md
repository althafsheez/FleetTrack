# Client-demo checklist

Initial planning checklist only. No demo steps have been independently runtime-verified by this audit. User reports backend is running. Record date, tester, test record IDs, observed result and evidence when each box is completed; omit sensitive data.

## Preparation

- [ ] Confirm `mvp` branch and approved implementation scope.
- [ ] TODO: confirm demo date/audience and reference screens.
- [ ] TODO: identify permitted MSSQL demo records and write/cleanup policy.
- [ ] Verify backend, database connectivity, affected endpoints and frontend build.
- [ ] Confirm required lookup/status values, pricing, transaction joins and posting rules.

## Main walkthrough

- [ ] Customer: search/select a real customer; create only if the demo requires it. TODO: mandatory fields.
- [ ] Vehicle: select a suitable available vehicle. TODO: verified availability rule.
- [ ] Tariff: display approved applicable pricing. TODO: precedence and calculation example.
- [ ] Contract: save agreed customer/vehicle/dates/terms and reopen it. TODO: numbering/defaults/actor and status values.
- [ ] Checkout: save handover time/km/fuel/location. TODO: required inspection evidence.
- [ ] Active Rental: show the checked-out rental in the active list with correct vehicle status.
- [ ] Fine/Salik if applicable: show correctly attributed charge and avoid duplicates. TODO: sample and allocation rule.
- [ ] Check-in: save return readings/time/location and verify agreed final charges and availability.
- [ ] Invoice: generate/reopen correct invoice, verify totals and required posting, show Sales Invoice Register.
- [ ] Receipt: record approved payment/allocation, verify balance and posting, show Receipt Register.

## Verification before presentation

- [ ] Reopen saved records to prove persistence, not merely a success message.
- [ ] Check missing record and invalid input handling for the demonstrated endpoints.
- [ ] Verify repeated submit does not duplicate rental/billing actions under the approved design.
- [ ] Compare linked records and balances against confirmed MSSQL/business expectations.
- [ ] Mark unimplemented or untested steps honestly; keep TODOs visible.
- [ ] TODO: agree how demo data is reset without deleting existing business data.

## Run record

Date/tester: TODO. Environment: TODO. Build/commit: TODO. Record references: TODO. Expected versus actual results: TODO. Remaining blockers: TODO.

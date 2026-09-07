# Initial user flows

This is the user-requested target flow, not a description of a working UI. Reference captures are not available. Candidate persistence paths below are hypotheses unless [RELATIONSHIPS.md](RELATIONSHIPS.md) says otherwise. Status values and formulas are deliberately unspecified.

| Step | Initial flow | Existing evidence | UNKNOWN / TODO |
| --- | --- | --- | --- |
| Customer selection | Search/list customers, select a record; create when needed. | Registered customer CRUD/search; group 26 ledger records. | Runtime verify; confirm required identity/license fields and duplicate handling. |
| Vehicle selection | Find a suitable available vehicle and select it. | Vehicle master mapping; supporting lookup GETs. | Complete vehicle API; establish availability/overlap rule and fleet status IDs. |
| Tariff selection | Select applicable rate and review charges. | Tariff group GET; group and customer tariff mappings. | Rate source precedence, duration units, discounts, optional charges, persistence. |
| Contract creation | Confirm customer, vehicle, dates and agreed terms, then save. | Contract master and vehicle-assignment mappings. | Required snapshots/defaults, numbering, status, actor/location and atomic writes. |
| Checkout | Record handover time, odometer, fuel and location. | Contract vehicle out-fields and checked-out actor field. | Required inspection evidence, status transition and assignment rules. |
| Active rental | List open rentals and inspect selected rental. | Candidate contract/vehicle status and date fields. | Authoritative active predicate, allowed actions, conflicts. |
| Fines/Salik | Review applicable charges and associate with the rental. | Fine/toll tables and invoicing flags. | Entry/import method, matching, markup/tax, duplicate prevention and late charges. |
| Check-in | Record return time, odometer, fuel and location; review charges. | Contract vehicle in-fields; actual end date and charge fields. | Duration/km/fuel calculations, closure and availability updates, DTIN meaning. |
| Invoicing | Review bill, finalize invoice, inspect Sales Invoice Register. | Sales master/details, staging, tax and posting candidates. | Accounting posting, numbering, rounding, staging requirement and repeat billing prevention. |
| Receipt | Record payment/allocation; inspect Receipt Register and remaining balance. | Receipt master/details and party balance candidates. | Settlement links, payment modes, partial payments/advances, numbering and posting. |

Validate this sequence against reference captures and a representative existing completed rental before implementing transaction writes. A missing detail is a TODO, not permission to invent a business rule.

"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FleetSidebar } from "@/components/fleet-sidebar";
import {
  getContract,
  getContractsPage,
  getCurrentUser,
  getLookup,
  logout,
  updateContract,
  type AuthenticatedUser,
  type ContractDetail,
  type ContractUpdate,
  type ContractViewRow,
  type LookupRecord,
} from "@/lib/api";

type DrawerMode = "view" | "edit";
type Option = { id: string; label: string };
type Lookups = Record<string, Option[]>;
type Value = string | number | boolean | null | undefined;

const pageSize = 10;
const lookupSpecs: [string, string, string, string[]][] = [
  ["contract-types", "contractTypes", "contractType", ["contractTypeName", "ContractTypeName"]],
  ["locations", "locations", "LocationId", ["LocationName"]],
  ["sales-persons", "salespeople", "employeeId", ["employeeName", "employeeCode"]],
  ["billing-types", "billingTypes", "invoiceTypeId", ["invoiceTypeName", "InvoiceType"]],
  ["visa-types", "visaTypes", "Id", ["VisaType"]],
  ["license-types", "licenseTypes", "DLTypeId", ["DLTypeName"]],
  ["nationalities", "nationalities", "NationalityId", ["NationalityName"]],
  ["fuel-levels", "fuelLevels", "FuelLevelId", ["FuelLevel"]],
  ["application-users", "appUsers", "UserID", ["DisplayName", "UserName"]],
  ["payment-modes", "paymentModes", "paymentMode", ["paymentModeName", "PaymentMode"]],
  ["discount-types", "discountTypes", "DiscountTypeId", ["DiscountTypeName"]],
];
const moneyFields = [
  ["Rate", "Base Rate"], ["CDW", "CDW Insurance"], ["PAI", "PAI Insurance"],
  ["DriverCharges", "Driver Charges"], ["AddDriverCharges", "Additional Driver"],
  ["ExcessKmCharge", "Excess KM Rate"], ["FuelCharges", "Fuel Charges"],
  ["SalikCharges", "Salik Tolls"], ["ExcessInsCharges", "Excess Insurance"],
  ["TrafficCharges", "Traffic Fines"], ["MileageCap", "Daily KM Cap"], ["OtherCharges", "Other Charges"],
] as const;

function toOptions(rows: LookupRecord[], idKey: string, labelKeys: string[]): Option[] {
  return rows.map((row) => {
    const rawId = row[idKey];
    const rawLabel = labelKeys.map((key) => row[key]).find((value) => value !== null && value !== undefined && value !== "");
    return { id: String(rawId ?? ""), label: String(rawLabel ?? rawId ?? "—") };
  }).filter((row) => row.id !== "");
}

function text(value: Value) { return value === null || value === undefined || value === "" ? "—" : String(value); }
function first(...values: Value[]) { return values.find((value) => value !== null && value !== undefined && value !== ""); }
function date(value: Value) {
  if (!value) return "—";
  const parsed = new Date(String(value));
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}
function dateTime(value: Value) {
  if (!value) return "—";
  const parsed = new Date(String(value));
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
function inputDate(value: Value, withTime = false) {
  if (!value) return "";
  const raw = String(value);
  return withTime ? raw.slice(0, 16) : raw.slice(0, 10);
}
function money(value: Value) { return Number(value ?? 0).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function lookupLabel(lookups: Lookups, key: string, value: Value) {
  return lookups[key]?.find((option) => option.id === String(value ?? ""))?.label ?? text(value);
}

function Detail({ label, value }: { label: string; value: React.ReactNode }) {
  return <p><small>{label}</small><b>{value || "—"}</b></p>;
}
function Input({ label, name, value, type = "text", required = false }: { label: string; name: string; value: Value; type?: string; required?: boolean }) {
  return <label>{label}{required && <em>*</em>}<input defaultValue={type.startsWith("date") ? inputDate(value, type === "datetime-local") : String(value ?? "")} name={name} required={required} step={type === "number" ? "any" : undefined} type={type} /></label>;
}
function Select({ label, name, value, rows }: { label: string; name: string; value: Value; rows?: Option[] }) {
  const current = String(value ?? "");
  const hasCurrent = !current || rows?.some((row) => row.id === current);
  return <label>{label}<select defaultValue={current} name={name}>{!current && <option value="">Not selected</option>}{!hasCurrent && <option value={current}>Legacy value: {current}</option>}{rows?.map((row, index) => <option key={`${name}-${row.id}-${index}`} value={row.id}>{row.label}</option>)}</select></label>;
}

function ContractDrawer({ detail, lookups, mode, saving, error, onClose, onEdit, onPrint, onSave }: {
  detail: ContractDetail; lookups: Lookups; mode: DrawerMode; saving: boolean; error: string | null;
  onClose: () => void; onEdit: () => void; onPrint: () => void; onSave: (form: HTMLFormElement) => void;
}) {
  const contract = detail.contract; const driver = detail.driver ?? {}; const vehicle = detail.vehicleAssignment ?? {};
  const c = (key: string) => contract[key] as Value; const d = (key: string) => driver[key] as Value; const v = (key: string) => vehicle[key] as Value;
  const title = text(c("CustomerName")); const agreement = text(c("ContractRefNo") ?? c("RTACode"));
  if (mode === "view") return <div className="cu-drawer-backdrop" role="presentation"><aside aria-label="Contract details" className="cu-drawer ct-drawer" role="dialog"><header><div><small>CONTRACT OVERVIEW · {agreement}</small><h2>{title}</h2></div><button aria-label="Close contract details" onClick={onClose} type="button">×</button></header><div className="ct-drawer-status"><span><i />Contract record</span><b>Agreement {agreement}</b></div><div className="cu-drawer-content cu-details ct-details">
    <section><h3><span>1</span> Agreement & Customer</h3><div><Detail label="Agreement No" value={agreement} /><Detail label="Customer" value={title} /><Detail label="Contract Type" value={lookupLabel(lookups, "contractTypes", c("ContractType"))} /><Detail label="Location" value={lookupLabel(lookups, "locations", c("ContractLocId"))} /><Detail label="Start Date" value={dateTime(c("ContractStartDate"))} /><Detail label="Expected End" value={dateTime(c("ContractExpectedEndDate"))} /><Detail label="Billing Cycle" value={lookupLabel(lookups, "billingTypes", c("BillingType"))} /><Detail label="Salesperson" value={lookupLabel(lookups, "salespeople", c("SalesPersonId"))} /></div></section>
    <section><h3><span>2</span> Primary Driver & Licence</h3><div><Detail label="Driver Name" value={text(first(d("UserName"), c("UserName")))} /><Detail label="Date of Birth" value={date(first(d("DateOfBirth"), c("DateOfBirth")))} /><Detail label="Mobile" value={text(first(d("Mobile"), c("Mobile")))} /><Detail label="Email" value={text(first(d("Email"), c("Email")))} /><Detail label="Nationality" value={lookupLabel(lookups, "nationalities", first(d("NationalityId"), c("Nationality")))} /><Detail label="Visa Type / Expiry" value={`${lookupLabel(lookups, "visaTypes", first(d("VisaType"), c("VisaType")))} · ${date(first(d("VisaExpiryDate"), c("VisaExpiryDate")))}`} /><Detail label="Licence Type / No." value={`${lookupLabel(lookups, "licenseTypes", first(d("DrivingLicenseType"), c("DrivingLicenseType")))} · ${text(first(d("DrivingLicenseNo"), c("DrivingLicenseNo")))}`} /><Detail label="Issue / Expiry" value={`${date(first(d("DLIssueDate"), c("DLIssueDate")))} · ${date(first(d("DLExpiryDate"), c("DLExpiryDate")))}`} /><Detail label="Place of Issue" value={text(first(d("DLPlaceOfIssue"), c("DLPlaceOfIssue")))} /><Detail label="Address" value={text(first(d("Address"), c("Address")))} /></div></section>
    <section><h3><span>3</span> Vehicle & Handover</h3><div><Detail label="Assigned Vehicle ID" value={text(v("VehicleId") ?? c("VehicleId"))} /><Detail label="Date/Time Out" value={dateTime(v("DatetimeOut"))} /><Detail label="Odometer Out" value={text(v("KmOut"))} /><Detail label="Fuel Level Out" value={lookupLabel(lookups, "fuelLevels", v("FuelLevelIdOut"))} /><Detail label="Checked Out By" value={lookupLabel(lookups, "appUsers", v("CheckedOutBy"))} /><Detail label="Handover Location" value={lookupLabel(lookups, "locations", v("LocationOut"))} /></div></section>
    <section><h3><span>4</span> Rates, Charges & Settlement</h3><div className="ct-money-details">{moneyFields.map(([key, label]) => <Detail key={key} label={label} value={`AED ${money(c(key))}`} />)}<Detail label="Discount" value={`AED ${money(c("Discount"))}`} /><Detail label="Advance Received" value={`AED ${money(c("Advance"))}`} /><Detail label="Subtotal" value={`AED ${money(c("Subtotal"))}`} /><Detail label="Payment Mode" value={lookupLabel(lookups, "paymentModes", c("PaymentMode"))} /></div></section>
    <section><h3><span>5</span> Notes</h3><div><Detail label="Confirmation Reference" value={text(c("ConfirmationRefValue"))} /><Detail label="Advance Invoice" value={c("IsAdvanceInvoice") ? "Required" : "Not required"} /><Detail label="Remarks" value={text(c("Remarks"))} /></div></section>
  </div><footer><button onClick={onPrint} type="button">Print Contract</button><button onClick={onClose} type="button">Close</button><button className="cu-primary" onClick={onEdit} type="button">Edit Contract</button></footer></aside></div>;

  return <div className="cu-drawer-backdrop" role="presentation"><aside aria-label="Edit contract" className="cu-drawer ct-drawer" role="dialog"><header><div><small>EDIT CONTRACT · {agreement}</small><h2>{title}</h2></div><button aria-label="Close contract editor" onClick={onClose} type="button">×</button></header><form className="cu-form ct-edit-form" onSubmit={(event) => { event.preventDefault(); onSave(event.currentTarget); }}><div className="cu-drawer-content">
    <div className="ct-locked"><b>Customer and vehicle assignment are locked</b><span>{title} · Vehicle ID {text(v("VehicleId") ?? c("VehicleId"))}</span></div>{error && <p className="cu-api-error">{error}</p>}
    <section><h3>1. Agreement</h3><div className="cu-form-grid"><Select label="Contract Type" name="ContractType" rows={lookups.contractTypes} value={c("ContractType")} /><Select label="Location" name="ContractLocId" rows={lookups.locations} value={c("ContractLocId")} /><Input label="Start Date/Time" name="ContractStartDate" type="datetime-local" value={c("ContractStartDate")} required /><Input label="Expected End" name="ContractExpectedEndDate" type="datetime-local" value={c("ContractExpectedEndDate")} required /><Select label="Billing Cycle" name="BillingType" rows={lookups.billingTypes} value={c("BillingType")} /><Select label="Salesperson" name="SalesPersonId" rows={lookups.salespeople} value={c("SalesPersonId")} /><Input label="Confirmation Reference" name="ConfirmationRefValue" value={c("ConfirmationRefValue")} /><label className="cu-check"><input defaultChecked={Boolean(c("IsAdvanceInvoice"))} name="IsAdvanceInvoice" type="checkbox" />Advance invoice required</label></div></section>
    <section><h3>2. Primary Driver & Licence</h3><div className="cu-form-grid"><Input label="Driver Name" name="UserName" value={first(d("UserName"), c("UserName"))} required /><Input label="Date of Birth" name="DateOfBirth" type="date" value={first(d("DateOfBirth"), c("DateOfBirth"))} /><Input label="Phone" name="Phone" value={first(d("Phone"), c("Phone"))} /><Input label="Mobile" name="Mobile" value={first(d("Mobile"), c("Mobile"))} /><Input label="Email" name="Email" type="email" value={first(d("Email"), c("Email"))} /><Select label="Nationality" name="Nationality" rows={lookups.nationalities} value={first(d("NationalityId"), c("Nationality"))} /><Input label="Address" name="Address" value={first(d("Address"), c("Address"))} /><Select label="Visa Type" name="VisaType" rows={lookups.visaTypes} value={first(d("VisaType"), c("VisaType"))} /><Input label="Visa Expiry" name="VisaExpiryDate" type="date" value={first(d("VisaExpiryDate"), c("VisaExpiryDate"))} /><Select label="Licence Type" name="DrivingLicenseType" rows={lookups.licenseTypes} value={first(d("DrivingLicenseType"), c("DrivingLicenseType"))} /><Input label="Licence Number" name="DrivingLicenseNo" value={first(d("DrivingLicenseNo"), c("DrivingLicenseNo"))} required /><Input label="Place of Issue" name="DLPlaceOfIssue" value={first(d("DLPlaceOfIssue"), c("DLPlaceOfIssue"))} required /><Input label="Licence Issue Date" name="DLIssueDate" type="date" value={first(d("DLIssueDate"), c("DLIssueDate"))} /><Input label="Licence Expiry" name="DLExpiryDate" type="date" value={first(d("DLExpiryDate"), c("DLExpiryDate"))} /></div></section>
    <section><h3>3. Vehicle Handover</h3><div className="cu-form-grid"><Input label="Date/Time Out" name="DatetimeOut" type="datetime-local" value={v("DatetimeOut")} /><Input label="Odometer Out" name="KmOut" type="number" value={v("KmOut")} /><Select label="Fuel Level Out" name="FuelLevelIdOut" rows={lookups.fuelLevels} value={v("FuelLevelIdOut")} /><Select label="Checked Out By" name="CheckedOutBy" rows={lookups.appUsers} value={v("CheckedOutBy")} /><Select label="Handover Location" name="LocationOut" rows={lookups.locations} value={v("LocationOut")} /></div></section>
    <section><h3>4. Rates, Charges & Settlement</h3><div className="ct-edit-money">{moneyFields.map(([key, label]) => <Input key={key} label={label} name={key} type="number" value={c(key)} />)}<Select label="Discount Type" name="DiscountType" rows={lookups.discountTypes} value={c("DiscountType")} /><Input label="Discount" name="Discount" type="number" value={c("Discount")} /><Input label="Advance Received" name="Advance" type="number" value={c("Advance")} /><Input label="Subtotal" name="Subtotal" type="number" value={c("Subtotal")} /><Select label="Payment Mode" name="PaymentMode" rows={lookups.paymentModes} value={c("PaymentMode")} /></div></section>
    <section><h3>5. Notes</h3><div className="cu-form-grid"><label className="cu-form-full">Remarks<textarea defaultValue={String(c("Remarks") ?? "")} name="Remarks" /></label></div></section>
  </div><footer><button disabled={saving} onClick={onClose} type="button">Cancel</button><button className="cu-primary" disabled={saving} type="submit">{saving ? "Saving…" : "Save Changes"}</button></footer></form></aside></div>;
}

export default function ContractListPage() {
  const router = useRouter(); const [user, setUser] = useState<AuthenticatedUser | null>(null); const [rows, setRows] = useState<ContractViewRow[]>([]); const [total, setTotal] = useState(0); const [offset, setOffset] = useState(0); const [loading, setLoading] = useState(true); const [error, setError] = useState<string | null>(null);
  const [customerName, setCustomerName] = useState(""); const [agreementNo, setAgreementNo] = useState(""); const [vehicle, setVehicle] = useState(""); const [filters, setFilters] = useState({ customerName: "", agreementNo: "", vehicle: "" });
  const [lookups, setLookups] = useState<Lookups>({}); const [drawer, setDrawer] = useState<DrawerMode | null>(null); const [detail, setDetail] = useState<ContractDetail | null>(null); const [detailLoading, setDetailLoading] = useState(false); const [saving, setSaving] = useState(false); const [drawerError, setDrawerError] = useState<string | null>(null);
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<number | null>(null);

  const loadPage = useCallback(async (nextOffset: number, activeFilters: { customerName?: string; agreementNo?: string; vehicle?: string }) => { setLoading(true); setError(null); try { const page = await getContractsPage(nextOffset, pageSize, activeFilters); setRows(page.items); setTotal(page.total); setOffset(page.offset); } catch (cause) { setError(cause instanceof Error ? cause.message : "Contract records could not be loaded."); } finally { setLoading(false); } }, []);
  useEffect(() => { async function load() { try { const activeUser = await getCurrentUser(); setUser(activeUser); const entries = await Promise.all(lookupSpecs.map(async ([path, key, id, labels]) => [key, toOptions(await getLookup(path), id, labels)] as const)); setLookups(Object.fromEntries(entries)); await loadPage(0, { customerName: "", agreementNo: "", vehicle: "" }); } catch (cause) { if (cause instanceof Error && cause.message.includes("session")) router.replace("/login"); else setError(cause instanceof Error ? cause.message : "Contract View could not be loaded."); setLoading(false); } } void load(); }, [loadPage, router]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize)); const currentPage = Math.floor(offset / pageSize) + 1;
  const pageNumbers = useMemo(() => { const first = Math.max(1, Math.min(currentPage - 2, totalPages - 4)); return Array.from({ length: Math.min(5, totalPages) }, (_, index) => first + index); }, [currentPage, totalPages]);
  async function openContract(contractId: number, mode: DrawerMode, assignmentId?: number | null) { setSelectedAssignmentId(assignmentId ?? null); setDrawer(mode); setDetail(null); setDrawerError(null); setDetailLoading(true); try { setDetail(await getContract(contractId)); } catch (cause) { setDrawerError(cause instanceof Error ? cause.message : "Contract details could not be loaded."); } finally { setDetailLoading(false); } }
  function printContract(contractId: number, assignmentId?: number | null) { if (!assignmentId) return; window.open(`/contracts/${contractId}/print?assignmentId=${assignmentId}`, "_blank", "noopener,noreferrer"); }
  function search() { const next = { customerName: customerName.trim(), agreementNo: agreementNo.trim(), vehicle: vehicle.trim() }; setFilters(next); void loadPage(0, next); }
  function clear() { const next = { customerName: "", agreementNo: "", vehicle: "" }; setCustomerName(""); setAgreementNo(""); setVehicle(""); setFilters(next); void loadPage(0, next); }
  async function save(form: HTMLFormElement) { if (!user || !detail) return; const data = new FormData(form); const optionalNumber = (name: string) => String(data.get(name) ?? "") === "" ? null : Number(data.get(name)); const optionalText = (name: string) => { const value = String(data.get(name) ?? "").trim(); return value || null; }; const draft: ContractUpdate = { UpdatedBy: user.userId, ContractType: optionalNumber("ContractType"), ContractLocId: optionalNumber("ContractLocId"), ContractStartDate: optionalText("ContractStartDate"), ContractExpectedEndDate: optionalText("ContractExpectedEndDate"), BillingType: optionalNumber("BillingType"), SalesPersonId: optionalNumber("SalesPersonId"), ConfirmationRefValue: optionalText("ConfirmationRefValue"), IsAdvanceInvoice: data.get("IsAdvanceInvoice") === "on", UserName: optionalText("UserName"), DateOfBirth: optionalText("DateOfBirth"), Phone: optionalText("Phone"), Mobile: optionalText("Mobile"), Email: optionalText("Email"), Address: optionalText("Address"), Nationality: optionalText("Nationality"), VisaType: optionalNumber("VisaType"), VisaExpiryDate: optionalText("VisaExpiryDate"), DrivingLicenseType: optionalNumber("DrivingLicenseType"), DrivingLicenseNo: optionalText("DrivingLicenseNo"), DLPlaceOfIssue: optionalText("DLPlaceOfIssue"), DLIssueDate: optionalText("DLIssueDate"), DLExpiryDate: optionalText("DLExpiryDate"), DatetimeOut: optionalText("DatetimeOut"), KmOut: optionalNumber("KmOut"), FuelLevelIdOut: optionalNumber("FuelLevelIdOut"), CheckedOutBy: optionalNumber("CheckedOutBy"), LocationOut: optionalNumber("LocationOut"), DiscountType: optionalNumber("DiscountType"), Discount: optionalNumber("Discount"), Advance: optionalNumber("Advance"), Subtotal: optionalNumber("Subtotal"), PaymentMode: optionalNumber("PaymentMode"), Remarks: optionalText("Remarks") }; for (const [name] of moneyFields) draft[name] = optionalNumber(name); const payload = Object.fromEntries(Object.entries(draft).filter(([, value]) => value !== null && value !== undefined)) as ContractUpdate; setSaving(true); setDrawerError(null); try { const updated = await updateContract(Number(detail.contract.ContractId), payload); setDetail(updated); setDrawer("view"); await loadPage(offset, filters); } catch (cause) { setDrawerError(cause instanceof Error ? cause.message : "Contract changes could not be saved."); } finally { setSaving(false); } }

  if (!user) return <main className="ft-loading">Loading FleetTrack contract register…</main>;
  return <div className="cu-app"><FleetSidebar /><div className="cu-frame"><header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Operations</span><span>/</span><strong>Contract View</strong></div><div className="cu-user"><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={() => { void logout().finally(() => router.replace("/login")); }} type="button">Logout</button></div></header><main className="cu-main ct-register"><div className="cu-page-heading"><div><h1>Contract List</h1><p>Search and review the live rental agreement register.</p></div></div>{error && <p className="cu-api-error">{error}</p>}
    <form className="cu-filter-panel ct-filter" onSubmit={(event) => { event.preventDefault(); search(); }}><div><label>Customer Name</label><input onChange={(event) => setCustomerName(event.target.value)} placeholder="Customer name" value={customerName} /></div><div><label>Agreement Number</label><input onChange={(event) => setAgreementNo(event.target.value)} placeholder="Agreement number" value={agreementNo} /></div><div><label>Vehicle</label><input onChange={(event) => setVehicle(event.target.value)} placeholder="Plate or fleet number" value={vehicle} /></div><button className="cu-filter-button" disabled={loading} type="submit">Search</button><button className="cu-clear" disabled={loading} onClick={clear} type="button">Clear</button></form>
    <div className="cu-list-meta"><span>{loading ? "Loading contract records…" : <>Showing <b>{total ? offset + 1 : 0}–{Math.min(offset + pageSize, total)}</b> of <b>{total}</b> contracts</>}</span><span>Live contract API</span></div>
    <section className="cu-table-card"><div className="cu-table-wrap"><table className="ct-table"><thead><tr><th>Actions</th><th>#</th><th>Agreement No.</th><th>Customer</th><th>Date Out</th><th>Date In</th><th>Days</th><th>Rate</th><th>Vehicle</th><th>Rent</th><th>Salik</th><th>Fine</th><th>Received</th><th>Pending</th></tr></thead><tbody>{!loading && rows.length === 0 && <tr><td className="ct-empty-row" colSpan={14}>No contracts match the selected filters.</td></tr>}{rows.map((row) => <tr key={row.assignmentId ?? `contract-${row.contractId}`}><td><div className="cu-actions"><button aria-label={`View agreement ${row.agreementNo}`} onClick={() => void openContract(row.contractId, "view", row.assignmentId)} title="View contract" type="button">◉</button><button aria-label={`Edit agreement ${row.agreementNo}`} onClick={() => void openContract(row.contractId, "edit", row.assignmentId)} title="Edit contract" type="button">✎</button><button aria-label={`Print agreement ${row.agreementNo}`} disabled={!row.assignmentId} onClick={() => printContract(row.contractId, row.assignmentId)} title={row.assignmentId ? "Print contract" : "No vehicle assignment to print"} type="button">⇧</button></div></td><td>{row.slNo}</td><td><code>{row.agreementNo}</code></td><td><b>{row.customer}</b></td><td>{date(row.dateOut)}</td><td>{date(row.dateIn)}</td><td>{row.totalDays}</td><td className="ct-money">{money(row.rate)}</td><td>{text(row.vehicle)}</td><td className="ct-money">{money(row.rent)}</td><td className="ct-money">{money(row.salik)}</td><td className="ct-money">{money(row.fine)}</td><td className="ct-money">{money(row.received)}</td><td className="ct-money ct-pending">{money(row.pendingAmount)}</td></tr>)}</tbody></table></div><footer className="cu-pagination"><span>Page {currentPage} of {totalPages}</span><div><button disabled={offset === 0 || loading} onClick={() => void loadPage(Math.max(0, offset - pageSize), filters)} type="button">Previous</button>{pageNumbers.map((page) => <button aria-current={page === currentPage ? "page" : undefined} className={page === currentPage ? "cu-page-active" : ""} disabled={loading || page === currentPage} key={page} onClick={() => void loadPage((page - 1) * pageSize, filters)} type="button">{page}</button>)}<button disabled={offset + pageSize >= total || loading} onClick={() => void loadPage(offset + pageSize, filters)} type="button">Next</button></div></footer></section>
  </main></div>{drawer && <>{detailLoading && <div className="cu-drawer-backdrop"><aside className="cu-drawer ct-drawer"><main className="ft-loading">Loading contract details…</main></aside></div>}{!detailLoading && !detail && <div className="cu-drawer-backdrop"><aside className="cu-drawer ct-drawer"><header><div><small>CONTRACT</small><h2>Unable to open record</h2></div><button onClick={() => setDrawer(null)} type="button">×</button></header><div className="cu-drawer-content">{drawerError && <p className="cu-api-error">{drawerError}</p>}</div></aside></div>}{detail && <ContractDrawer detail={detail} error={drawerError} lookups={lookups} mode={drawer} onClose={() => { setDrawer(null); setDetail(null); setDrawerError(null); setSelectedAssignmentId(null); }} onEdit={() => { setDrawerError(null); setDrawer("edit"); }} onPrint={() => printContract(Number(detail.contract.ContractId), selectedAssignmentId)} onSave={(form) => void save(form)} saving={saving} />}</>}</div>;
}

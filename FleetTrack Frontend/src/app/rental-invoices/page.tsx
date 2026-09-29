"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FleetSidebar } from "@/components/fleet-sidebar";
import {
  createRentalInvoice,
  deleteRentalInvoice,
  getCurrentUser,
  getDueRentalInvoices,
  getInvoiceLookup,
  getSalesInvoicesPage,
  logout,
  previewRentalInvoice,
  type AuthenticatedUser,
  type InvoiceLookup,
  type RentalInvoiceDueRow,
  type RentalInvoicePreview,
  type RentalInvoiceSettings,
  type SalesInvoiceRegisterRow,
} from "@/lib/api";

const pageSize = 10;

function money(value: string | number | null | undefined) {
  return Number(value ?? 0).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function date(value: string | null | undefined) {
  if (!value) return "-";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}
function dateTime(value: string | null | undefined) {
  if (!value) return "-";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
function invoiceNumber(row: SalesInvoiceRegisterRow) {
  return row.invoiceNo || row.voucherNo || `Draft ${row.salesMasterId}`;
}
function dueTone(nextInvoiceDate: string) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(nextInvoiceDate);
  due.setHours(0, 0, 0, 0);
  if (due.getTime() < today.getTime()) return "overdue";
  if (due.getTime() === today.getTime()) return "due";
  return "scheduled";
}

function Select({ label, name, rows, required = false }: { label: string; name: string; rows: InvoiceLookup[]; required?: boolean }) {
  return <label>{label}<select name={name} required={required}><option value="">Select {label}</option>{rows.map((row) => <option key={row.id} value={row.id}>{row.currencySymbol ? `${row.name} · ${row.currencySymbol}` : row.name}</option>)}</select></label>;
}

export default function RentalInvoicesPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [dueRows, setDueRows] = useState<RentalInvoiceDueRow[]>([]);
  const [registerRows, setRegisterRows] = useState<SalesInvoiceRegisterRow[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [q, setQ] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [salesAccounts, setSalesAccounts] = useState<InvoiceLookup[]>([]);
  const [exchangeRates, setExchangeRates] = useState<InvoiceLookup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [selected, setSelected] = useState<RentalInvoiceDueRow | null>(null);
  const [preview, setPreview] = useState<RentalInvoicePreview | null>(null);
  const [invoiceDraft, setInvoiceDraft] = useState<SalesInvoiceRegisterRow | null>(null);
  const [drawerError, setDrawerError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

  const loadRegister = useCallback(async (nextOffset = offset, search = q) => {
    const page = await getSalesInvoicesPage(nextOffset, pageSize, { q: search, invoiceType: "rental", posted: "" });
    setRegisterRows(page.items);
    setTotal(page.total);
    setOffset(page.offset);
  }, [offset, q]);

  const loadDue = useCallback(async () => {
    setDueRows(await getDueRentalInvoices(asOfDate ? `${asOfDate}T00:00:00` : undefined));
  }, [asOfDate]);

  useEffect(() => {
    async function load() {
      try {
        setUser(await getCurrentUser());
        const [due, accounts, rates, register] = await Promise.all([
          getDueRentalInvoices(),
          getInvoiceLookup("sales-accounts"),
          getInvoiceLookup("exchange-rates"),
          getSalesInvoicesPage(0, pageSize, { invoiceType: "rental", posted: "" }),
        ]);
        setDueRows(due);
        setSalesAccounts(accounts);
        setExchangeRates(rates);
        setRegisterRows(register.items);
        setTotal(register.total);
        setOffset(register.offset);
      } catch (cause) {
        if (cause instanceof Error && cause.message.includes("session")) router.replace("/login");
        else setError(cause instanceof Error ? cause.message : "Rental invoices could not be loaded.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [router]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.floor(offset / pageSize) + 1;
  const pageNumbers = useMemo(() => {
    const first = Math.max(1, Math.min(currentPage - 2, totalPages - 4));
    return Array.from({ length: Math.min(5, totalPages) }, (_, index) => first + index);
  }, [currentPage, totalPages]);

  function settings(form: HTMLFormElement): RentalInvoiceSettings | null {
    const data = new FormData(form);
    const salesAccountId = Number(data.get("salesAccountId") || 0);
    const exchangeRateId = Number(data.get("exchangeRateId") || 0);
    if (!salesAccountId || !exchangeRateId) {
      setDrawerError("Select a sales account and exchange rate.");
      return null;
    }
    return {
      salesAccountId,
      exchangeRateId,
      creditPeriod: Number(data.get("creditPeriod") || 0),
      lpoNo: String(data.get("lpoNo") || "").trim() || null,
    };
  }

  async function openPreview(row: RentalInvoiceDueRow, form: HTMLFormElement) {
    const payload = settings(form);
    if (!payload) return;
    setWorking(true);
    setDrawerError(null);
    setInvoiceDraft(null);
    try {
      setPreview(await previewRentalInvoice(row.contractId, { ...payload, asOfDate: asOfDate ? `${asOfDate}T00:00:00` : null }));
    } catch (cause) {
      setDrawerError(cause instanceof Error ? cause.message : "Rental invoice preview failed.");
    } finally {
      setWorking(false);
    }
  }

  async function createDraft(row: RentalInvoiceDueRow, form: HTMLFormElement) {
    const payload = settings(form);
    if (!payload) return;
    setWorking(true);
    setDrawerError(null);
    try {
      const invoice = await createRentalInvoice(row.contractId, { ...payload, asOfDate: asOfDate ? `${asOfDate}T00:00:00` : null });
      setInvoiceDraft(invoice);
      setNotice(`Rental Invoice draft ${invoice.invoiceNo || invoice.voucherNo || invoice.salesMasterId} created for agreement ${row.contractRefNo}.`);
      await Promise.all([loadDue(), loadRegister(0, q)]);
    } catch (cause) {
      setDrawerError(cause instanceof Error ? cause.message : "Rental Invoice draft could not be created.");
    } finally {
      setWorking(false);
    }
  }

  async function deleteLatest(row: RentalInvoiceDueRow) {
    const latest = registerRows.find((item) => item.contractRefNo === row.contractRefNo && item.isPosted !== true);
    if (!latest) {
      setDrawerError("No unposted rental draft for this agreement is visible in the current register.");
      return;
    }
    if (!window.confirm(`Delete latest draft ${invoiceNumber(latest)} for agreement ${row.contractRefNo}?`)) return;
    setWorking(true);
    setDrawerError(null);
    try {
      await deleteRentalInvoice(row.contractId, latest.salesMasterId);
      setInvoiceDraft(null);
      setPreview(null);
      setNotice(`Deleted draft ${invoiceNumber(latest)} and restored the contract schedule.`);
      await Promise.all([loadDue(), loadRegister(0, q)]);
    } catch (cause) {
      setDrawerError(cause instanceof Error ? cause.message : "Latest draft could not be deleted.");
    } finally {
      setWorking(false);
    }
  }

  if (!user) return <main className="ft-loading">Loading Rental Invoice workspace...</main>;

  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Billing</span><span>/</span><strong>Rental Invoices</strong></div><div className="cu-user"><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={() => { void logout().finally(() => router.replace("/login")); }} type="button">Logout</button></div></header>
    <main className="cu-main ri-main"><div className="cu-page-heading"><div><h1>Rental Invoices</h1><p>Review due Monthly, Weekly, and Lease contracts before creating draft rental invoices.</p></div><button className="cu-primary" disabled={loading} onClick={() => { setLoading(true); setError(null); Promise.all([loadDue(), loadRegister(0, q)]).catch((cause) => setError(cause instanceof Error ? cause.message : "Refresh failed.")).finally(() => setLoading(false)); }} type="button">Refresh</button></div>
      {error && <p className="cu-api-error">{error}</p>}{notice && <p className="ri-notice">{notice}</p>}
      <section className="ri-workspace">
        <div className="ri-due">
          <form className="cu-filter-panel ri-filter" onSubmit={(event) => { event.preventDefault(); void loadDue(); }}><div><label>As of date</label><input onChange={(event) => setAsOfDate(event.target.value)} type="date" value={asOfDate} /></div><button className="cu-filter-button" type="submit">Load Due</button><button className="cu-clear" onClick={() => { setAsOfDate(""); void getDueRentalInvoices().then(setDueRows); }} type="button">Today</button></form>
          <div className="cu-list-meta"><span>{loading ? "Loading due rentals..." : <><b>{dueRows.length}</b> contracts due for rental invoice review</>}</span><span>GET /rental-invoices/due</span></div>
          <section className="cu-table-card"><div className="cu-table-wrap"><table className="ri-due-table"><thead><tr><th>Actions</th><th>Agreement</th><th>Customer</th><th>Billing</th><th>Next Invoice</th><th>Status</th></tr></thead><tbody>{!loading && dueRows.length === 0 && <tr><td className="ri-empty" colSpan={6}>No due rental invoices for the selected date.</td></tr>}{dueRows.map((row) => <tr key={row.contractId}><td><div className="cu-actions"><button onClick={() => { setSelected(row); setPreview(null); setInvoiceDraft(null); setDrawerError(null); }} title="Preview invoice" type="button">◉</button><button onClick={() => router.push(`/contracts/list?agreementNo=${encodeURIComponent(row.contractRefNo)}`)} title="Open contract register" type="button">⇥</button></div></td><td><code>{row.contractRefNo}</code></td><td><b>{row.customerName || "-"}</b><small>Customer ID {row.customerId ?? "-"}</small></td><td>Type {row.contractType}<small>Payment {row.paymentType} · Billing {row.billingType ?? "-"}</small></td><td>{date(row.nextInvoiceDate)}</td><td><span className={`ri-status ${dueTone(row.nextInvoiceDate)}`}>{dueTone(row.nextInvoiceDate)}</span></td></tr>)}</tbody></table></div></section>
        </div>
        <div className="ri-register">
          <form className="cu-filter-panel ri-filter" onSubmit={(event) => { event.preventDefault(); void loadRegister(0, q); }}><div><label>Sales Invoice Search</label><input onChange={(event) => setQ(event.target.value)} placeholder="Invoice, agreement, customer..." value={q} /></div><button className="cu-filter-button" type="submit">Search</button><button className="cu-clear" onClick={() => { setQ(""); void loadRegister(0, ""); }} type="button">Clear</button></form>
          <div className="cu-list-meta"><span>Showing <b>{total ? offset + 1 : 0}-{Math.min(offset + pageSize, total)}</b> of <b>{total}</b> rental drafts</span><span>Sales Invoice Register</span></div>
          <section className="cu-table-card"><div className="cu-table-wrap"><table className="ri-register-table"><thead><tr><th>Draft</th><th>Date</th><th>Agreement</th><th>Customer</th><th>Vehicles</th><th>Total</th><th>Status</th></tr></thead><tbody>{registerRows.length === 0 && <tr><td className="ri-empty" colSpan={7}>No rental invoice drafts match the filter.</td></tr>}{registerRows.map((row) => <tr key={row.salesMasterId}><td><code>{invoiceNumber(row)}</code></td><td>{date(row.invoiceDate)}</td><td>{row.contractRefNo || "-"}</td><td><b>{row.customerName || "-"}</b></td><td>{row.vehicleNos || "-"}</td><td className="ri-money">AED {money(row.grandTotal)}</td><td><span className={`ri-status ${row.isPosted ? "posted" : "draft"}`}>{row.isPosted ? "posted" : "draft"}</span></td></tr>)}</tbody></table></div><footer className="cu-pagination"><span>Page {currentPage} of {totalPages}</span><div><button disabled={offset === 0} onClick={() => void loadRegister(Math.max(0, offset - pageSize), q)} type="button">Previous</button>{pageNumbers.map((page) => <button className={page === currentPage ? "cu-page-active" : ""} disabled={page === currentPage} key={page} onClick={() => void loadRegister((page - 1) * pageSize, q)} type="button">{page}</button>)}<button disabled={offset + pageSize >= total} onClick={() => void loadRegister(offset + pageSize, q)} type="button">Next</button></div></footer></section>
        </div>
      </section>
    </main>
  </div>{selected && <div className="cu-drawer-backdrop"><aside className="cu-drawer ri-drawer"><header><div><small>RENTAL INVOICE PREVIEW</small><h2>Agreement {selected.contractRefNo}</h2></div><button onClick={() => setSelected(null)} type="button">×</button></header><form className="cu-form" id="rental-invoice-form" onSubmit={(event) => { event.preventDefault(); void openPreview(selected, event.currentTarget); }}><div className="cu-drawer-content">
    {drawerError && <p className="cu-api-error">{drawerError}</p>}
    <section><h3>1. Billing Settings</h3><div className="cu-form-grid"><Select label="Sales Account" name="salesAccountId" required rows={salesAccounts} /><Select label="Exchange Rate" name="exchangeRateId" required rows={exchangeRates} /><label>Credit Period<input defaultValue="0" min="0" name="creditPeriod" type="number" /></label><label>LPO Number<input name="lpoNo" /></label></div></section>
    <section><h3>2. Schedule</h3><div className="ri-schedule"><p><small>Customer</small><b>{selected.customerName || "-"}</b></p><p><small>Next invoice date</small><b>{dateTime(selected.nextInvoiceDate)}</b></p><p><small>Due status</small><b>{dueTone(selected.nextInvoiceDate)}</b></p></div></section>
    {preview && <section><h3>3. Preview Lines</h3><div className="ri-preview-head"><p><small>Period</small><b>{date(preview.periodStart)} - {date(preview.periodEnd)}</b></p><p><small>Next schedule</small><b>{date(preview.nextInvoiceDate)}</b></p><p><small>Grand total</small><b>AED {money(preview.grandTotal)}</b></p></div><table className="ri-preview-lines"><thead><tr><th>Item</th><th>Description</th><th>Qty</th><th>Rate</th><th>Tax</th><th>Amount</th></tr></thead><tbody>{preview.lines.map((line, index) => <tr key={`${line.itemTypeId}-${index}`}><td>{line.itemTypeName}</td><td>{line.description}</td><td>{line.quantity}</td><td>{money(line.rate)}</td><td>{money(line.taxAmount)}</td><td>{money(line.amount)}</td></tr>)}</tbody></table></section>}
    {invoiceDraft && <section><h3>4. Created Draft</h3><div className="ri-created"><b>{invoiceNumber(invoiceDraft)}</b><span>AED {money(invoiceDraft.grandTotal)}</span></div></section>}
  </div><footer><button disabled={working} onClick={() => setSelected(null)} type="button">Close</button><button disabled={working} form="rental-invoice-form" type="submit">Preview</button><button className="cu-primary" disabled={working} onClick={(event) => { const form = event.currentTarget.form; if (form) void createDraft(selected, form); }} type="button">{working ? "Working..." : "Create Draft"}</button><button disabled={working} onClick={() => void deleteLatest(selected)} type="button">Delete Latest Draft</button></footer></form></aside></div>}</div>;
}

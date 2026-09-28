"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FleetSidebar } from "@/components/fleet-sidebar";
import {
  ApiError,
  createContraVoucher,
  deleteContraVoucher,
  getContraAccounts,
  getContraExchangeRates,
  getContraNumberingRule,
  getContraPrintData,
  getContraVoucher,
  getContraVouchersPage,
  getCurrentUser,
  logout,
  updateContraVoucher,
  type AuthenticatedUser,
  type ContraAccount,
  type ContraDirection,
  type ContraExchangeRate,
  type ContraNumberingRule,
  type ContraRegisterFilters,
  type ContraVoucherPayload,
  type ContraVoucherRegisterRow,
  type ContraVoucherResponse,
} from "@/lib/api";

const PAGE_SIZE = 25;
const EMPTY_FILTERS: ContraRegisterFilters = { fromDate: "", toDate: "", direction: "", ledgerId: "", voucherNo: "" };

type EditorLine = {
  key: string;
  contraDetailsId?: number;
  ledgerId: string;
  amount: string;
  exchangeRateId: string;
  chequeNo: string;
  chequeDate: string;
};

type EditorState = {
  mode: "create" | "edit";
  voucher?: ContraVoucherResponse;
  direction: ContraDirection;
  voucherDate: string;
  headerLedgerId: string;
  manualVoucherNo: string;
  narration: string;
  idempotencyKey: string;
  lines: EditorLine[];
};

type BalanceWarning = { payload: ContraVoucherPayload; printAfter: boolean; message: string; ledgers: string[] };

function inputDate(value = new Date()) {
  const local = new Date(value.getTime() - value.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function apiDate(value: string) {
  return `${value}T00:00:00`;
}

function displayDate(value: string | null | undefined) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function money(value: string | number | null | undefined) {
  return Number(value ?? 0).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function lineKey() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

function newLine(exchangeRateId = ""): EditorLine {
  return { key: lineKey(), ledgerId: "", amount: "", exchangeRateId, chequeNo: "", chequeDate: "" };
}

function escapeHtml(value: unknown) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  }[character] ?? character));
}

function printVoucher(voucher: ContraVoucherResponse, target: Window) {
  const rows = voucher.lines.map((line, index) => `<tr><td>${index + 1}</td><td>${escapeHtml(line.ledgerName || line.ledgerId)}</td><td>${escapeHtml(line.currencySymbol || line.currencyName || "-")}</td><td class="amount">${money(line.amount)}</td><td>${escapeHtml(line.chequeNo || "-")}</td><td>${displayDate(line.chequeDate)}</td></tr>`).join("");
  target.document.open();
  target.document.write(`<!doctype html><html><head><title>Contra Voucher ${escapeHtml(voucher.invoiceNo)}</title><style>body{font:12px Arial,sans-serif;color:#0b1c30;margin:32px}h1{font-size:22px;margin:0 0 4px}p{margin:4px 0}.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0;padding:12px;border:1px solid #c6c6cd}.meta b{display:block;margin-top:3px}table{width:100%;border-collapse:collapse;margin-top:18px}th,td{padding:8px;border:1px solid #c6c6cd;text-align:left}th{background:#f8f9ff}.amount{text-align:right}.total{margin-top:18px;text-align:right;font-size:18px;font-weight:bold}.narration{margin-top:18px;padding:12px;border:1px solid #c6c6cd}@media print{button{display:none}}</style></head><body><h1>Contra Voucher</h1><p>FleetTrack</p><div class="meta"><div>Voucher No.<b>${escapeHtml(voucher.invoiceNo)}</b></div><div>Date<b>${displayDate(voucher.voucherDate)}</b></div><div>Direction<b>${escapeHtml(voucher.direction === "deposit" ? "Deposit" : "Withdrawal")}</b></div><div>Bank/Cash A/C<b>${escapeHtml(voucher.headerLedgerName || voucher.headerLedgerId)}</b></div></div><table><thead><tr><th>#</th><th>Bank/Cash A/C</th><th>Currency</th><th class="amount">Amount</th><th>Cheque No.</th><th>Cheque Date</th></tr></thead><tbody>${rows}</tbody></table><div class="narration"><b>Narration</b><p>${escapeHtml(voucher.narration || "-")}</p></div><div class="total">Total: ${money(voucher.totalAmount)}</div><script>window.addEventListener('load',()=>window.print())<\/script></body></html>`);
  target.document.close();
}

function errorMessage(cause: unknown, fallback: string) {
  return cause instanceof Error ? cause.message : fallback;
}

function openPrintWindow() {
  const target = window.open("", "_blank");
  if (target) target.opener = null;
  return target;
}

export default function ContraVouchersPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [accounts, setAccounts] = useState<ContraAccount[]>([]);
  const [rows, setRows] = useState<ContraVoucherRegisterRow[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [filters, setFilters] = useState<ContraRegisterFilters>(EMPTY_FILTERS);
  const [activeFilters, setActiveFilters] = useState<ContraRegisterFilters>(EMPTY_FILTERS);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [editorLoading, setEditorLoading] = useState(false);
  const [editorError, setEditorError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [rates, setRates] = useState<ContraExchangeRate[]>([]);
  const [numbering, setNumbering] = useState<ContraNumberingRule | null>(null);
  const [balanceWarning, setBalanceWarning] = useState<BalanceWarning | null>(null);

  const loadPage = useCallback(async (nextOffset: number, nextFilters: ContraRegisterFilters) => {
    const page = await getContraVouchersPage(nextOffset, PAGE_SIZE, nextFilters);
    setRows(page.items);
    setTotal(page.total);
    setOffset(page.offset);
  }, []);

  useEffect(() => {
    async function load() {
      try {
        const [currentUser, accountRows, page] = await Promise.all([
          getCurrentUser(), getContraAccounts(), getContraVouchersPage(0, PAGE_SIZE),
        ]);
        setUser(currentUser);
        setAccounts(accountRows);
        setRows(page.items);
        setTotal(page.total);
        setOffset(page.offset);
      } catch (cause) {
        if (cause instanceof ApiError && cause.status === 401) router.replace("/login");
        else setPageError(errorMessage(cause, "Contra Vouchers could not be loaded."));
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [router]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const pageNumbers = useMemo(() => {
    const first = Math.max(1, Math.min(currentPage - 2, Math.max(1, totalPages - 4)));
    return Array.from({ length: Math.min(5, totalPages) }, (_, index) => first + index);
  }, [currentPage, totalPages]);

  const defaultRateId = rates[0]?.id ? String(rates[0].id) : "";
  const baseCurrency = rates.find((rate) => Number(rate.rate) === 1)?.currencySymbol || "AED";
  const editorTotal = useMemo(() => editor?.lines.reduce((sum, line) => {
    const rate = rates.find((item) => item.id === Number(line.exchangeRateId));
    return sum + Number(line.amount || 0) * Number(rate?.rate || 0);
  }, 0) ?? 0, [editor, rates]);

  async function searchRegister(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setPageError(null);
    setActiveFilters(filters);
    try { await loadPage(0, filters); }
    catch (cause) { setPageError(errorMessage(cause, "Contra Voucher search failed.")); }
    finally { setLoading(false); }
  }

  async function clearFilters() {
    setFilters(EMPTY_FILTERS);
    setActiveFilters(EMPTY_FILTERS);
    setLoading(true);
    setPageError(null);
    try { await loadPage(0, EMPTY_FILTERS); }
    catch (cause) { setPageError(errorMessage(cause, "Contra Vouchers could not be loaded.")); }
    finally { setLoading(false); }
  }

  async function changePage(nextOffset: number) {
    setLoading(true);
    setPageError(null);
    try { await loadPage(nextOffset, activeFilters); }
    catch (cause) { setPageError(errorMessage(cause, "The requested page could not be loaded.")); }
    finally { setLoading(false); }
  }

  async function openCreate() {
    const voucherDate = inputDate();
    setEditorLoading(true);
    setEditorError(null);
    setEditor({
      mode: "create", direction: "deposit", voucherDate, headerLedgerId: "", manualVoucherNo: "", narration: "",
      idempotencyKey: lineKey(), lines: [newLine()],
    });
    try {
      const [rateRows, rule] = await Promise.all([getContraExchangeRates(voucherDate), getContraNumberingRule(voucherDate)]);
      setRates(rateRows);
      setNumbering(rule);
      setEditor((current) => current ? { ...current, lines: current.lines.map((line) => ({ ...line, exchangeRateId: line.exchangeRateId || String(rateRows[0]?.id || "") })) } : current);
    } catch (cause) {
      setEditorError(errorMessage(cause, "Contra Voucher settings could not be loaded."));
    } finally {
      setEditorLoading(false);
    }
  }

  async function openEdit(row: ContraVoucherRegisterRow) {
    const voucherDate = row.voucherDate.slice(0, 10);
    setEditorLoading(true);
    setEditorError(null);
    setEditor({ mode: "edit", direction: row.direction, voucherDate, headerLedgerId: String(row.headerLedgerId), manualVoucherNo: "", narration: row.narration || "", idempotencyKey: "", lines: [] });
    try {
      const [voucher, rateRows, rule] = await Promise.all([
        getContraVoucher(row.contraMasterId), getContraExchangeRates(voucherDate), getContraNumberingRule(voucherDate),
      ]);
      setRates(rateRows);
      setNumbering(rule);
      setEditor({
        mode: "edit", voucher, direction: voucher.direction, voucherDate, headerLedgerId: String(voucher.headerLedgerId),
        manualVoucherNo: rule.automatic ? "" : voucher.invoiceNo, narration: voucher.narration || "", idempotencyKey: voucher.idempotencyKey || "",
        lines: voucher.lines.map((line) => ({
          key: lineKey(), contraDetailsId: line.contraDetailsId, ledgerId: String(line.ledgerId), amount: String(line.amount),
          exchangeRateId: String(line.exchangeRateId), chequeNo: line.chequeNo || "", chequeDate: line.chequeDate?.slice(0, 10) || "",
        })),
      });
    } catch (cause) {
      setEditorError(errorMessage(cause, "Contra Voucher details could not be loaded."));
    } finally {
      setEditorLoading(false);
    }
  }

  async function changeVoucherDate(voucherDate: string) {
    setEditor((current) => current ? { ...current, voucherDate } : current);
    if (!voucherDate) return;
    setEditorLoading(true);
    setEditorError(null);
    try {
      const [rateRows, rule] = await Promise.all([getContraExchangeRates(voucherDate), getContraNumberingRule(voucherDate)]);
      setRates(rateRows);
      setNumbering(rule);
      setEditor((current) => current ? {
        ...current,
        manualVoucherNo: rule.automatic ? "" : current.manualVoucherNo,
        lines: current.lines.map((line) => ({ ...line, exchangeRateId: rateRows.some((rate) => rate.id === Number(line.exchangeRateId)) ? line.exchangeRateId : String(rateRows[0]?.id || "") })),
      } : current);
    } catch (cause) {
      setEditorError(errorMessage(cause, "Numbering and exchange rates are unavailable for this date."));
    } finally {
      setEditorLoading(false);
    }
  }

  function updateLine(key: string, change: Partial<EditorLine>) {
    setEditor((current) => current ? { ...current, lines: current.lines.map((line) => line.key === key ? { ...line, ...change } : line) } : current);
  }

  function selectLineAccount(line: EditorLine, ledgerId: string) {
    const account = accounts.find((item) => item.id === Number(ledgerId));
    updateLine(line.key, account?.isBank ? { ledgerId } : { ledgerId, chequeNo: "", chequeDate: "" });
  }

  function buildPayload(confirmNegativeBalance: boolean): ContraVoucherPayload | null {
    if (!editor) return null;
    setEditorError(null);
    if (!editor.voucherDate || !editor.headerLedgerId) {
      setEditorError("Select a voucher date and Bank/Cash account.");
      return null;
    }
    if (!numbering) {
      setEditorError("Voucher numbering is not available for the selected date.");
      return null;
    }
    if (!numbering.automatic && !editor.manualVoucherNo.trim()) {
      setEditorError("Enter the manual voucher number.");
      return null;
    }
    if (!editor.lines.length) {
      setEditorError("Add at least one Bank/Cash account line.");
      return null;
    }
    for (const line of editor.lines) {
      if (!line.ledgerId || !line.exchangeRateId || Number(line.amount) <= 0) {
        setEditorError("Every line requires an account, currency, and amount greater than zero.");
        return null;
      }
      if (line.ledgerId === editor.headerLedgerId) {
        setEditorError("A detail account cannot be the same as the header Bank/Cash account.");
        return null;
      }
      if (Boolean(line.chequeNo.trim()) !== Boolean(line.chequeDate)) {
        setEditorError("Cheque number and cheque date must be entered together.");
        return null;
      }
    }
    return {
      voucherDate: apiDate(editor.voucherDate), direction: editor.direction, headerLedgerId: Number(editor.headerLedgerId),
      manualVoucherNo: numbering.automatic ? null : editor.manualVoucherNo.trim(), narration: editor.narration.trim() || null,
      idempotencyKey: editor.mode === "create" ? editor.idempotencyKey : null, confirmNegativeBalance,
      lines: editor.lines.map((line) => ({
        contraDetailsId: line.contraDetailsId ?? null, ledgerId: Number(line.ledgerId), amount: Number(line.amount).toFixed(5),
        exchangeRateId: Number(line.exchangeRateId), chequeNo: line.chequeNo.trim() || null, chequeDate: line.chequeDate ? apiDate(line.chequeDate) : null,
      })),
    };
  }

  async function executeSave(payload: ContraVoucherPayload, printAfter: boolean) {
    if (!editor) return;
    const printTarget = printAfter ? openPrintWindow() : null;
    setWorking(true);
    setEditorError(null);
    try {
      const saved = editor.mode === "create"
        ? await createContraVoucher(payload)
        : await updateContraVoucher(editor.voucher!.contraMasterId, payload);
      setNotice(`${editor.mode === "create" ? "Created" : "Updated"} Contra Voucher ${saved.invoiceNo}.`);
      setEditor(null);
      setBalanceWarning(null);
      await loadPage(offset, activeFilters);
      if (printTarget) printVoucher(saved, printTarget);
    } catch (cause) {
      printTarget?.close();
      if (cause instanceof ApiError && cause.code === "NEGATIVE_CASH_BALANCE") {
        if (cause.canConfirm) setBalanceWarning({ payload, printAfter, message: cause.message, ledgers: cause.ledgers });
        else setEditorError(`${cause.message}${cause.ledgers.length ? `: ${cause.ledgers.join(", ")}` : ""}. Saving is blocked by policy.`);
      } else {
        setEditorError(errorMessage(cause, "Contra Voucher could not be saved."));
      }
    } finally {
      setWorking(false);
    }
  }

  function submitEditor(printAfter: boolean) {
    const payload = buildPayload(false);
    if (payload) void executeSave(payload, printAfter);
  }

  async function confirmNegativeBalance() {
    if (!balanceWarning) return;
    const warning = balanceWarning;
    setBalanceWarning(null);
    await executeSave({ ...warning.payload, confirmNegativeBalance: true }, warning.printAfter);
  }

  async function removeVoucher() {
    if (!editor?.voucher) return;
    if (!window.confirm(`Delete Contra Voucher ${editor.voucher.invoiceNo} for ${money(editor.voucher.totalAmount)}? This also removes its ledger postings.`)) return;
    setWorking(true);
    setEditorError(null);
    try {
      await deleteContraVoucher(editor.voucher.contraMasterId);
      const nextTotal = Math.max(0, total - 1);
      const nextOffset = offset >= nextTotal ? Math.max(0, offset - PAGE_SIZE) : offset;
      setEditor(null);
      setNotice(`Deleted Contra Voucher ${editor.voucher.invoiceNo}.`);
      await loadPage(nextOffset, activeFilters);
    } catch (cause) {
      setEditorError(errorMessage(cause, "Contra Voucher could not be deleted."));
    } finally {
      setWorking(false);
    }
  }

  async function openPrint(id: number) {
    const target = openPrintWindow();
    if (!target) {
      setPageError("Allow pop-ups to print the Contra Voucher.");
      return;
    }
    try { printVoucher(await getContraPrintData(id), target); }
    catch (cause) { target.close(); setPageError(errorMessage(cause, "Print data could not be loaded.")); }
  }

  if (!user) return <main className="ft-loading">{pageError || "Loading Contra Vouchers..."}</main>;

  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Financial Accounts</span><span>/</span><strong>Contra Vouchers</strong></div><div className="cu-user"><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={() => { void logout().finally(() => router.replace("/login")); }} type="button">Logout</button></div></header>
    <main className="cu-main cv-main">
      <section className="cv-heading"><div><div><h1>Contra Vouchers</h1><span>{total} Records</span></div><p>Cash and bank transfers recorded through the existing accounting workflow.</p></div><button className="cv-primary" onClick={() => void openCreate()} type="button">+ New Contra Voucher</button></section>
      {pageError && <p className="cu-api-error">{pageError}</p>}{notice && <p className="cv-notice">{notice}<button onClick={() => setNotice(null)} type="button">×</button></p>}
      <form className="cv-filters" onSubmit={searchRegister}>
        <label>From Date<input onChange={(event) => setFilters({ ...filters, fromDate: event.target.value })} type="date" value={filters.fromDate || ""} /></label>
        <label>To Date<input onChange={(event) => setFilters({ ...filters, toDate: event.target.value })} type="date" value={filters.toDate || ""} /></label>
        <fieldset><legend>Direction</legend><div className="cv-segments">{(["", "deposit", "withdrawal"] as const).map((value) => <button className={filters.direction === value ? "active" : ""} key={value || "all"} onClick={() => setFilters({ ...filters, direction: value })} type="button">{value ? value[0].toUpperCase() + value.slice(1) : "All"}</button>)}</div></fieldset>
        <label>Bank/Cash Account<select onChange={(event) => setFilters({ ...filters, ledgerId: event.target.value ? Number(event.target.value) : "" })} value={filters.ledgerId || ""}><option value="">All Accounts</option>{accounts.map((account) => <option key={account.id} value={account.id}>{account.name}</option>)}</select></label>
        <label>Voucher Number<input onChange={(event) => setFilters({ ...filters, voucherNo: event.target.value })} placeholder="Search voucher..." value={filters.voucherNo || ""} /></label>
        <div className="cv-filter-actions"><button className="cv-primary cv-icon-action" disabled={loading} title="Search" type="submit">Search</button><button className="cv-secondary cv-icon-action" disabled={loading} onClick={() => void clearFilters()} title="Clear filters" type="button">Clear</button></div>
      </form>
      <section className="cv-register">
        <div className="cv-table-wrap"><table><thead><tr><th>Voucher No.</th><th>Date</th><th>Direction</th><th>Bank/Cash Account</th><th>Offset Accounts</th><th>Narration</th><th>Lines</th><th className="number">Total Amount</th><th>Actions</th></tr></thead><tbody>
          {!loading && rows.length === 0 && <tr><td className="cv-empty" colSpan={9}>No Contra Vouchers match the selected filters.</td></tr>}
          {rows.map((row) => <tr key={row.contraMasterId}><td><button className="cv-voucher-link" onClick={() => void openEdit(row)} type="button">{row.invoiceNo || row.voucherNo}</button></td><td>{displayDate(row.voucherDate)}</td><td><span className={`cv-direction ${row.direction}`}>{row.direction === "deposit" ? "↓ Deposit" : "↑ Withdrawal"}</span></td><td><b>{row.headerLedgerName || `Ledger ${row.headerLedgerId}`}</b></td><td><span className="cv-offsets" title={row.offsetAccountNames.join(", ")}>{row.offsetAccountNames.length ? row.offsetAccountNames.join(", ") : "-"}</span></td><td><span className="cv-narration" title={row.narration || ""}>{row.narration || "-"}</span></td><td className="center">{row.lineCount}</td><td className="number"><small>{baseCurrency}</small>{money(row.totalAmount)}</td><td><div className="cv-row-actions"><button onClick={() => void openEdit(row)} title="Edit voucher" type="button">Edit</button><button onClick={() => void openPrint(row.contraMasterId)} title="Print voucher" type="button">Print</button></div></td></tr>)}
        </tbody></table></div>
        <footer className="cv-pagination"><span>Showing <b>{total ? offset + 1 : 0}-{Math.min(offset + PAGE_SIZE, total)}</b> of <b>{total}</b></span><div><button disabled={offset === 0 || loading} onClick={() => void changePage(Math.max(0, offset - PAGE_SIZE))} type="button">Previous</button>{pageNumbers.map((page) => <button className={page === currentPage ? "active" : ""} disabled={page === currentPage || loading} key={page} onClick={() => void changePage((page - 1) * PAGE_SIZE)} type="button">{page}</button>)}<button disabled={offset + PAGE_SIZE >= total || loading} onClick={() => void changePage(offset + PAGE_SIZE)} type="button">Next</button></div></footer>
      </section>
    </main>
  </div>
  {editor && <div className="cv-modal-backdrop" role="presentation"><section aria-labelledby="cv-editor-title" aria-modal="true" className="cv-modal" role="dialog">
    <header><div><h2 id="cv-editor-title">{editor.mode === "create" ? "New Contra Voucher" : "Edit Contra Voucher"}</h2><p>{editor.mode === "create" ? "Record a transfer between cash and bank accounts." : `Voucher ${editor.voucher?.invoiceNo || ""}`}</p></div><button aria-label="Close" disabled={working} onClick={() => setEditor(null)} type="button">×</button></header>
    <div className="cv-modal-body">{editorError && <p className="cu-api-error">{editorError}</p>}{editorLoading && <p className="cv-loading">Loading voucher settings...</p>}
      <section className="cv-voucher-head">
        <fieldset><legend>Transfer Direction</legend><div className="cv-segments"><button className={editor.direction === "deposit" ? "active" : ""} onClick={() => setEditor({ ...editor, direction: "deposit" })} type="button">↓ Deposit</button><button className={editor.direction === "withdrawal" ? "active" : ""} onClick={() => setEditor({ ...editor, direction: "withdrawal" })} type="button">↑ Withdrawal</button></div></fieldset>
        <label>Voucher No.<input disabled={editor.mode === "edit" || numbering?.automatic} onChange={(event) => setEditor({ ...editor, manualVoucherNo: event.target.value })} placeholder={numbering?.automatic ? "Automatic" : "Enter number"} readOnly={editor.mode === "edit" || numbering?.automatic} value={editor.mode === "edit" ? editor.voucher?.invoiceNo || "" : numbering?.automatic ? numbering.nextInvoiceNo || "" : editor.manualVoucherNo} /></label>
        <label>Voucher Date<input onChange={(event) => void changeVoucherDate(event.target.value)} type="date" value={editor.voucherDate} /></label>
        <label>Bank/Cash A/C<select onChange={(event) => setEditor({ ...editor, headerLedgerId: event.target.value })} value={editor.headerLedgerId}><option value="">Select account</option>{accounts.map((account) => <option key={account.id} value={account.id}>{account.name}</option>)}</select></label>
      </section>
      <section className="cv-lines"><header><h3>{editor.direction === "deposit" ? "Source Bank/Cash Accounts" : "Destination Bank/Cash Accounts"}</h3><span>{editor.lines.length} {editor.lines.length === 1 ? "line" : "lines"}</span></header><div className="cv-lines-scroll"><table><thead><tr><th>#</th><th>Bank/Cash Account</th><th>Currency</th><th className="number">Amount</th><th className="number">Base Amount</th><th>Cheque No.</th><th>Cheque Date</th><th>Action</th></tr></thead><tbody>{editor.lines.map((line, index) => {
        const account = accounts.find((item) => item.id === Number(line.ledgerId));
        const rate = rates.find((item) => item.id === Number(line.exchangeRateId));
        return <tr key={line.key}><td className="center">{index + 1}</td><td><select onChange={(event) => selectLineAccount(line, event.target.value)} value={line.ledgerId}><option value="">Select account</option>{accounts.filter((item) => item.id !== Number(editor.headerLedgerId)).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></td><td><select onChange={(event) => updateLine(line.key, { exchangeRateId: event.target.value })} value={line.exchangeRateId || defaultRateId}><option value="">Currency</option>{rates.map((item) => <option key={item.id} value={item.id}>{item.currencySymbol || item.currencyName || item.currencyId}</option>)}</select></td><td><input className="number" min="0.00001" onChange={(event) => updateLine(line.key, { amount: event.target.value })} placeholder="0.00" step="0.00001" type="number" value={line.amount} /></td><td className="number cv-base-amount">{money(Number(line.amount || 0) * Number(rate?.rate || 0))}</td><td><input disabled={!account?.isBank} onChange={(event) => updateLine(line.key, { chequeNo: event.target.value })} placeholder={account?.isBank ? "Cheque no." : "-"} value={line.chequeNo} /></td><td><input disabled={!account?.isBank} onChange={(event) => updateLine(line.key, { chequeDate: event.target.value })} type="date" value={line.chequeDate} /></td><td className="center"><button className="cv-remove-line" disabled={editor.lines.length === 1} onClick={() => setEditor({ ...editor, lines: editor.lines.filter((item) => item.key !== line.key) })} title="Remove line" type="button">×</button></td></tr>;
      })}</tbody></table></div><footer><button className="cv-secondary" onClick={() => setEditor({ ...editor, lines: [...editor.lines, newLine(String(rates[0]?.id || ""))] })} type="button">+ Add Line</button></footer></section>
      <section className="cv-voucher-bottom"><label>Voucher Narration<textarea maxLength={2000} onChange={(event) => setEditor({ ...editor, narration: event.target.value })} placeholder="Enter narration..." rows={4} value={editor.narration} /></label><aside><div><span>Total Lines</span><b>{editor.lines.length}</b></div><div><span>Base Currency</span><b>{baseCurrency}</b></div><strong><span>Total Voucher Amount</span><b>{money(editorTotal)} <small>{baseCurrency}</small></b></strong></aside></section>
    </div>
    <footer className="cv-modal-actions"><div>{editor.mode === "edit" && <button className="cv-danger" disabled={working} onClick={() => void removeVoucher()} type="button">Delete</button>}<button className="cv-secondary" disabled={working} onClick={() => editor.mode === "create" ? void openCreate() : void openEdit(editor.voucher!)} type="button">Reset</button></div><div><button className="cv-secondary" disabled={working} onClick={() => setEditor(null)} type="button">Close</button><button className="cv-secondary cv-blue-outline" disabled={working || editorLoading} onClick={() => submitEditor(true)} type="button">{editor.mode === "create" ? "Save & Print" : "Update & Print"}</button><button className="cv-primary" disabled={working || editorLoading} onClick={() => submitEditor(false)} type="button">{working ? "Saving..." : editor.mode === "create" ? "Save Voucher" : "Update Voucher"}</button></div></footer>
  </section></div>}
  {balanceWarning && <div className="cv-confirm-backdrop"><section aria-modal="true" className="cv-confirm" role="alertdialog"><h2>Negative balance warning</h2><p>{balanceWarning.message}</p><ul>{balanceWarning.ledgers.map((ledger) => <li key={ledger}>{ledger}</li>)}</ul><p>Continue saving this voucher?</p><div><button className="cv-secondary" disabled={working} onClick={() => setBalanceWarning(null)} type="button">Cancel</button><button className="cv-primary" disabled={working} onClick={() => void confirmNegativeBalance()} type="button">Continue Anyway</button></div></section></div>}
  </div>;
}

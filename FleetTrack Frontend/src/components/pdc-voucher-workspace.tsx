"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FleetSidebar } from "@/components/fleet-sidebar";
import {
  ApiError, createPDCVoucher, deletePDCVoucher, getCurrentUser, getPDCLookups,
  getPDCNumberingRule, getPDCOpenReferences, getPDCPrintData, getPDCVoucher,
  getPDCVouchersPage, logout, updatePDCVoucher, type AuthenticatedUser,
  type PDCAllocationInput, type PDCLookup, type PDCNumberingRule, type PDCOpenReference,
  type PDCRegisterFilters, type PDCSourceType, type PDCVoucherPayload,
  type PDCVoucherRegisterRow, type PDCVoucherResponse,
} from "@/lib/api";

const PAGE_SIZE = 25;
const EMPTY_FILTERS: PDCRegisterFilters = { fromDate: "", toDate: "", voucherNo: "", ledgerId: "", bankId: "", amount: "", chequeNo: "", status: "" };
type Allocation = PDCAllocationInput & { pendingAmount: number; sourceLabel: string; sourceTypeName: string; currencySymbol: string };
type Editor = { mode: "create" | "edit"; voucher?: PDCVoucherResponse; voucherDate: string; chequeDate: string; manualVoucherNo: string; partyLedgerId: string; controlLedgerId: string; bankLedgerId: string; chequeNo: string; narration: string; idempotencyKey: string; amount: string; allocations: Allocation[] };

function inputDate(value = new Date()) { const local = new Date(value.getTime() - value.getTimezoneOffset() * 60000); return local.toISOString().slice(0, 10); }
function apiDate(value: string) { return `${value}T00:00:00`; }
function displayDate(value?: string | null) { if (!value) return "-"; const date = new Date(value); return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }); }
function money(value?: string | number | null) { return Number(value ?? 0).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function makeKey() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }
function errorText(error: unknown, fallback: string) { return error instanceof Error ? error.message : fallback; }
function escapeHtml(value: unknown) { return String(value ?? "").replace(/[&<>'"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[c] ?? c)); }

function printVoucher(voucher: PDCVoucherResponse, target: Window) {
  const rows = voucher.allocations.map((row, index) => `<tr><td>${index + 1}</td><td>${escapeHtml(row.ledgerName || row.ledgerId)}</td><td>${escapeHtml(row.sourceVoucherTypeName || "Reference")}</td><td>${escapeHtml(row.sourceInvoiceNo || row.sourceVoucherNo)}</td><td class="num">AED ${money(row.amount)}</td>
</tr>`).join("");
  const html = `<!doctype html><html><head><title>${escapeHtml(voucher.voucherTypeName)} ${escapeHtml(voucher.invoiceNo)}</title><style>body{margin:32px;color:#0b1c30;font:12px Arial}h1{margin:0}.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0;padding:12px;border:1px solid #c6c6cd}.meta b{display:block;margin-top:4px}table{width:100%;border-collapse:collapse}th,td{padding:8px;border:1px solid #c6c6cd;text-align:left}th{background:#f8f9ff}.num{text-align:right}.total{margin-top:18px;text-align:right;font-size:18px;font-weight:bold}</style>
</head><body><h1>${escapeHtml(voucher.voucherTypeName)}</h1><p>FleetTrack</p><div class="meta"><div>Voucher No.<b>${escapeHtml(voucher.invoiceNo)}</b>
</div><div>Voucher Date<b>${displayDate(voucher.voucherDate)}</b>
</div><div>Cheque Date<b>${displayDate(voucher.chequeDate)}</b>
</div><div>Bank<b>${escapeHtml(voucher.bankLedgerName)}</b>
</div><div>Cheque No.<b>${escapeHtml(voucher.chequeNo)}</b>
</div><div>Status<b>${escapeHtml(voucher.status)}</b>
</div>
</div><table><thead><tr><th>#</th><th>Account Ledger</th><th>Source Type</th><th>Reference</th><th class="num">Allocation</th>
</tr>
</thead><tbody>${rows}</tbody>
</table><div class="total">Total: AED ${money(voucher.amount)}</div><script>window.addEventListener('load',()=>window.print())<\/script>
</body>
</html>`;
  const url = URL.createObjectURL(new Blob([html], { type: "text/html" }));
  target.location.href = url;
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

export function PDCVoucherWorkspace({ kind }: { kind: PDCSourceType }) {
  const router = useRouter(); const payable = kind === "payable"; const title = payable ? "PDC Payables" : "PDC Receivables"; const partyLabel = "Party Account";
  const [user, setUser] = useState<AuthenticatedUser | null>(null); const [rows, setRows] = useState<PDCVoucherRegisterRow[]>([]); const [total, setTotal] = useState(0); const [offset, setOffset] = useState(0);
  const [filters, setFilters] = useState<PDCRegisterFilters>(EMPTY_FILTERS); const [activeFilters, setActiveFilters] = useState<PDCRegisterFilters>(EMPTY_FILTERS);
  const [parties, setParties] = useState<PDCLookup[]>([]); const [banks, setBanks] = useState<PDCLookup[]>([]); const [controls, setControls] = useState<PDCLookup[]>([]); const [numbering, setNumbering] = useState<PDCNumberingRule | null>(null); const [accountSearch, setAccountSearch] = useState(""); const [controlSearch, setControlSearch] = useState("");
  const [editor, setEditor] = useState<Editor | null>(null); const [references, setReferences] = useState<PDCOpenReference[]>([]); const [allocationOpen, setAllocationOpen] = useState(false);
  const [loading, setLoading] = useState(true); const [working, setWorking] = useState(false); const [pageError, setPageError] = useState<string | null>(null); const [editorError, setEditorError] = useState<string | null>(null); const [allocationError, setAllocationError] = useState<string | null>(null); const [notice, setNotice] = useState<string | null>(null);

  const loadPage = useCallback(async (nextOffset: number, nextFilters: PDCRegisterFilters) => { setLoading(true); setPageError(null); try { const page = await getPDCVouchersPage(kind, nextOffset, PAGE_SIZE, nextFilters); setRows(page.items); setTotal(page.total); setOffset(page.offset); } catch (error) { if (error instanceof ApiError && error.status === 401) router.replace("/login"); else setPageError(errorText(error, `${title} could not be loaded.`)); } finally { setLoading(false); } }, [kind, router, title]);
  useEffect(() => { void (async () => { try { const [me, partyRows, bankRows, controlRows] = await Promise.all([getCurrentUser(), getPDCLookups(kind, "accounts"), getPDCLookups(kind, "banks"), getPDCLookups(kind, "accounts")]); setUser(me); setParties(partyRows); setBanks(bankRows); setControls(controlRows); await loadPage(0, EMPTY_FILTERS); } catch (error) { if (error instanceof ApiError && error.status === 401) router.replace("/login"); else setPageError(errorText(error, `${title} setup could not be loaded.`)); setLoading(false); } })(); }, [kind, loadPage, router, title]);

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE)); const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const pageNumbers = useMemo(() => Array.from({ length: Math.min(5, pages) }, (_, index) => Math.min(Math.max(1, currentPage - 2), Math.max(1, pages - 4)) + index).filter((page) => page <= pages), [currentPage, pages]);
  const amount = Number(editor?.amount || 0);
  const allocatedAmount = editor?.allocations.reduce((total, item) => total + Number(item.amount), 0) || 0;
  const selectedParty = parties.find((item) => item.id === Number(editor?.partyLedgerId));

  async function openCreate() { const voucherDate = inputDate(); setEditorError(null); setAllocationOpen(false); setReferences([]); setAccountSearch(""); setControlSearch(""); setEditor({ mode: "create", voucherDate, chequeDate: voucherDate, manualVoucherNo: "", partyLedgerId: "", controlLedgerId: "", bankLedgerId: "", chequeNo: "", narration: "", idempotencyKey: makeKey(), amount: "", allocations: [] }); try { setNumbering(await getPDCNumberingRule(kind, voucherDate)); } catch (error) { setEditorError(errorText(error, "Voucher numbering could not be loaded.")); } }
  async function openEdit(row: PDCVoucherRegisterRow) { setEditorError(null); setAllocationOpen(false); try { const voucher = await getPDCVoucher(kind, row.id); setEditor({ mode: "edit", voucher, voucherDate: inputDate(new Date(voucher.voucherDate)), chequeDate: inputDate(new Date(voucher.chequeDate)), manualVoucherNo: voucher.invoiceNo, partyLedgerId: voucher.partyLedgerId ? String(voucher.partyLedgerId) : "", controlLedgerId: String(voucher.controlLedgerId), bankLedgerId: String(voucher.bankLedgerId), chequeNo: voucher.chequeNo, narration: voucher.narration || "", idempotencyKey: voucher.idempotencyKey || "", amount: String(voucher.amount), allocations: voucher.allocations.map((item) => ({ ...item, pendingAmount: Number(item.amount), sourceLabel: item.sourceInvoiceNo || item.sourceVoucherNo, sourceTypeName: item.sourceVoucherTypeName || "Reference", currencySymbol: "AED" })) }); setNumbering(await getPDCNumberingRule(kind, inputDate(new Date(voucher.voucherDate)))); } catch (error) { setPageError(errorText(error, `${title.slice(0, -1)} detail could not be loaded.`)); } }
  async function changeVoucherDate(value: string) { if (!editor) return; setEditor({ ...editor, voucherDate: value, chequeDate: editor.chequeDate < value ? value : editor.chequeDate }); try { setNumbering(await getPDCNumberingRule(kind, value)); } catch (error) { setEditorError(errorText(error, "Voucher numbering could not be loaded.")); } }
  async function chooseParty(value: string) { if (!editor) return; setEditor({ ...editor, partyLedgerId: value, allocations: [] }); setReferences([]); if (!value) return; try { setReferences(await getPDCOpenReferences(kind, Number(value))); } catch (error) { setAllocationError(errorText(error, "Open references could not be loaded for this Party Account.")); } }
  async function searchAccounts(value: string) { setAccountSearch(value); try { setParties(await getPDCLookups(kind, "accounts", value)); } catch (error) { setEditorError(errorText(error, "Account Ledger search could not be loaded.")); } }
  async function searchControls(value: string) { setControlSearch(value); try { setControls(await getPDCLookups(kind, "accounts", value)); } catch (error) { setEditorError(errorText(error, "Account Ledger search could not be loaded.")); } }
  async function showAllocations() { if (!editor) return; setAllocationError(null); setAllocationOpen(true); if (!editor.partyLedgerId) return; try { setReferences(await getPDCOpenReferences(kind, Number(editor.partyLedgerId))); } catch (error) { setAllocationError(errorText(error, "Open references could not be loaded for this Party Account.")); } }
  function addReference(value: string) { if (!editor || !value) return; const [type, ...number] = value.split("|"); const reference = references.find((item) => item.sourceVoucherTypeId === Number(type) && item.sourceVoucherNo === number.join("|")); if (!reference || editor.allocations.some((item) => item.sourceVoucherTypeId === reference.sourceVoucherTypeId && item.sourceVoucherNo === reference.sourceVoucherNo)) return; setEditor({ ...editor, allocations: [...editor.allocations, { ledgerId: reference.ledgerId, sourceVoucherTypeId: reference.sourceVoucherTypeId, sourceVoucherNo: reference.sourceVoucherNo, amount: String(reference.pendingAmount), pendingAmount: Number(reference.pendingAmount), sourceLabel: reference.sourceInvoiceNo || reference.sourceVoucherNo, sourceTypeName: reference.sourceVoucherTypeName || "Reference", currencySymbol: reference.currencySymbol || "AED" }] }); }
  function updateAllocation(index: number, value: string) { if (!editor) return; setEditor({ ...editor, allocations: editor.allocations.map((item, itemIndex) => itemIndex === index ? { ...item, amount: value } : item) }); }
  function removeAllocation(index: number) { if (!editor) return; setEditor({ ...editor, allocations: editor.allocations.filter((_, itemIndex) => itemIndex !== index) }); }
  function validateAllocations() { if (!editor?.allocations.length) { setAllocationError("Select at least one open reference."); return false; } if (editor.allocations.some((item) => Number(item.amount) <= 0 || Number(item.amount) > item.pendingAmount)) { setAllocationError("Every allocation must be positive and cannot exceed its pending amount."); return false; } if (editor.allocations.reduce((total, item) => total + Number(item.amount), 0).toFixed(5) !== amount.toFixed(5)) { setAllocationError("Against allocations must equal the PDC amount."); return false; } setAllocationOpen(false); return true; }
  function buildPayload(): PDCVoucherPayload | null { if (!editor) return null; setEditorError(null); const allocated = editor.allocations.reduce((total, item) => total + Number(item.amount), 0); if (!editor.voucherDate || !editor.chequeDate || !editor.controlLedgerId || !editor.bankLedgerId || !editor.partyLedgerId || !editor.chequeNo.trim() || amount <= 0) { setEditorError("Complete the voucher date, Account Ledger, bank, cheque number, amount, and Against reference."); return null; } if (!editor.allocations.length || allocated.toFixed(5) !== amount.toFixed(5)) { setEditorError("Select Against references whose total equals the cheque amount."); return null; } if (editor.chequeDate < editor.voucherDate) { setEditorError("Cheque date cannot be earlier than voucher date."); return null; } if (!numbering?.automatic && !editor.manualVoucherNo.trim()) { setEditorError("Enter the manual voucher number."); return null; } return { voucherDate: apiDate(editor.voucherDate), controlLedgerId: Number(editor.controlLedgerId), partyLedgerId: Number(editor.partyLedgerId), bankLedgerId: Number(editor.bankLedgerId), amount: amount.toFixed(5), chequeNo: editor.chequeNo.trim(), chequeDate: apiDate(editor.chequeDate), manualVoucherNo: numbering?.automatic ? null : editor.manualVoucherNo.trim(), narration: editor.narration.trim() || null, idempotencyKey: editor.mode === "create" ? editor.idempotencyKey : editor.voucher?.idempotencyKey || null, allocations: editor.allocations.map(({ ledgerId, sourceVoucherTypeId, sourceVoucherNo, amount: allocationAmount }) => ({ ledgerId, sourceVoucherTypeId, sourceVoucherNo, amount: allocationAmount })) }; }
  async function save(printAfter: boolean) { if (!editor) return; const payload = buildPayload(); if (!payload) return; const target = printAfter ? window.open("", "_blank") : null; setWorking(true); try { const saved = editor.mode === "create" ? await createPDCVoucher(kind, payload) : await updatePDCVoucher(kind, editor.voucher!.id, payload); setNotice(`${saved.voucherTypeName} ${saved.invoiceNo} ${editor.mode === "create" ? "created" : "updated"}.`); setEditor(null); await loadPage(offset, activeFilters); if (target) printVoucher(saved, target); } catch (error) { target?.close(); setEditorError(errorText(error, `${title.slice(0, -1)} could not be saved.`)); } finally { setWorking(false); } }
  async function remove() { if (!editor?.voucher || !window.confirm(`Delete ${editor.voucher.invoiceNo}? This reverses its accounting entries.`)) return; setWorking(true); try { await deletePDCVoucher(kind, editor.voucher.id); setNotice(`${editor.voucher.invoiceNo} deleted.`); setEditor(null); await loadPage(0, activeFilters); } catch (error) { setEditorError(errorText(error, "The PDC could not be deleted.")); } finally { setWorking(false); } }
  async function print(id: number) { const target = window.open("", "_blank"); if (!target) { setPageError("Allow pop-ups to print this voucher."); return; } try { printVoucher(await getPDCPrintData(kind, id), target); } catch (error) { target.close(); setPageError(errorText(error, "Print data could not be loaded.")); } }
  function search(event: FormEvent) { event.preventDefault(); setActiveFilters({ ...filters }); void loadPage(0, filters); }
  function clearFilters() { setFilters(EMPTY_FILTERS); setActiveFilters(EMPTY_FILTERS); void loadPage(0, EMPTY_FILTERS); }

  if (!user) return <main className="ft-loading">{pageError || `Loading ${title}...`}</main>;
  return <div className="cu-app"><FleetSidebar /><div className="cu-frame"><header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Financial Accounts</span><span>/</span><strong>{title}</strong>
</div><div className="cu-user"><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small>
</span><button className="cu-logout" onClick={() => void logout().finally(() => router.replace("/login"))} type="button">Logout</button>
</div>
</header>
    <main className="cu-main pdc-main"><section className="cv-heading"><div><div><h1>{title}</h1><span>{total} Records</span>
</div><p>{payable ? "Manage post-dated cheques, account references, and bank clearance." : "Manage post-dated cheques, account references, and bank clearance."}</p>
</div><button className="cv-primary" onClick={() => void openCreate()} type="button">+ New PDC {payable ? "Payable" : "Receivable"}</button>
</section>
      {pageError && <p className="cu-api-error">{pageError}</p>}{notice && <p className="cv-notice">{notice}<button onClick={() => setNotice(null)} type="button">×</button>
</p>}
      <form className="pdc-filters" onSubmit={search}><label>From Date<input type="date" value={filters.fromDate || ""} onChange={(e) => setFilters({ ...filters, fromDate: e.target.value })} />
</label><label>To Date<input type="date" value={filters.toDate || ""} onChange={(e) => setFilters({ ...filters, toDate: e.target.value })} />
</label><label>Account Ledger<select value={filters.ledgerId || ""} onChange={(e) => setFilters({ ...filters, ledgerId: e.target.value ? Number(e.target.value) : "" })}><option value="">All Ledgers</option>{controls.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
</label><label>Voucher Number<input placeholder="Search voucher..." value={filters.voucherNo || ""} onChange={(e) => setFilters({ ...filters, voucherNo: e.target.value })} />
</label><label>Cheque Number<input placeholder="Search cheque..." value={filters.chequeNo || ""} onChange={(e) => setFilters({ ...filters, chequeNo: e.target.value })} />
</label><label>Status<select value={filters.status || ""} onChange={(e) => setFilters({ ...filters, status: e.target.value })}><option value="">All Statuses</option><option>Pending</option><option>Cleared</option><option>Bounced</option>
</select>
</label><div className="pdc-filter-actions"><button className="cv-primary" disabled={loading} type="submit">Search</button><button className="cv-secondary" disabled={loading} onClick={clearFilters} type="button">Reset</button>
</div>
</form>
      <section className="cv-register"><div className="cv-table-wrap"><table className="pdc-table"><thead><tr><th>Voucher No.</th><th>Voucher Type</th><th>Voucher Date</th><th>Cheque Date</th><th>Amount</th><th>Narration</th><th>Account Ledger</th><th>Status</th><th>Actions</th>
</tr>
</thead><tbody>{!loading && !rows.length && <tr><td className="cv-empty" colSpan={9}>No {title} match the selected filters.</td>
</tr>}{rows.map((row) => <tr key={row.id}><td><button className="cv-voucher-link" onClick={() => void openEdit(row)} type="button">{row.invoiceNo}</button>
</td><td>{row.voucherTypeName}</td><td>{displayDate(row.voucherDate)}</td><td>{displayDate(row.chequeDate)}</td><td className="pdc-money"><small>AED</small> {money(row.amount)}</td><td><span className="pdc-ellipsis" title={row.narration || ""}>{row.narration || "-"}</span>
</td><td><b>{row.controlLedgerName || "Unknown account ledger"}</b>
</td><td><span className={`pdc-status ${row.status.toLowerCase()}`}>{row.status}</span>
</td><td><div className="cv-row-actions"><button aria-label="View" title="View" onClick={() => void openEdit(row)} type="button">◉</button>{row.status === "Pending" && <button aria-label="Edit" title="Edit" onClick={() => void openEdit(row)} type="button">✎</button>}<button aria-label="Print" title="Print" onClick={() => void print(row.id)} type="button">▣</button>
</div>
</td>
</tr>)}</tbody>
</table>
</div><footer className="cv-pagination"><span>Showing <b>{total ? offset + 1 : 0}-{Math.min(offset + PAGE_SIZE, total)}</b> of <b>{total}</b>
</span><div><button disabled={!offset || loading} onClick={() => void loadPage(Math.max(0, offset - PAGE_SIZE), activeFilters)} type="button">Previous</button>{pageNumbers.map((page) => <button className={page === currentPage ? "active" : ""} disabled={page === currentPage || loading} key={page} onClick={() => void loadPage((page - 1) * PAGE_SIZE, activeFilters)} type="button">{page}</button>)}<button disabled={offset + PAGE_SIZE >= total || loading} onClick={() => void loadPage(offset + PAGE_SIZE, activeFilters)} type="button">Next</button>
</div>
</footer>
</section>
    </main>
</div>
    {editor && <div className="cv-modal-backdrop"><section className="cv-modal pdc-editor" role="dialog" aria-modal="true"><header><div><h2>{editor.mode === "create" ? "New" : editor.voucher?.status === "Pending" ? "Edit" : "View"} PDC {payable ? "Payable" : "Receivable"}</h2><p>{payable ? "Post-dated cheque registration." : "Post-dated cheque registration."}</p>
</div><button aria-label="Close" disabled={working} onClick={() => setEditor(null)} type="button">×</button>
</header><div className="cv-modal-body">{editorError && <p className="cu-api-error">{editorError}</p>}<section className="pdc-form-grid"><label>Voucher Number<input disabled={editor.mode === "edit" || Boolean(numbering?.automatic)} value={editor.mode === "edit" ? editor.voucher?.invoiceNo || "" : numbering?.automatic ? numbering.nextInvoiceNo || "" : editor.manualVoucherNo} onChange={(e) => setEditor({ ...editor, manualVoucherNo: e.target.value })} />
</label><label>Voucher Date *<input disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} type="date" value={editor.voucherDate} onChange={(e) => void changeVoucherDate(e.target.value)} />
</label><label>Cheque Date *<input disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} min={editor.voucherDate} type="date" value={editor.chequeDate} onChange={(e) => setEditor({ ...editor, chequeDate: e.target.value })} />
</label><label>Account Ledger Search<input placeholder="Search all accounts..." type="search" value={controlSearch} onChange={(e) => void searchControls(e.target.value)} /></label><label>Account Ledger *<select disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} value={editor.controlLedgerId} onChange={(e) => setEditor({ ...editor, controlLedgerId: e.target.value })}><option value="">Select account ledger</option>{controls.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
</label><label>Amount (AED)<div className="pdc-money-input"><span>AED</span><input min="0.01" step="0.01" type="number" value={editor.amount} onChange={(e) => setEditor({ ...editor, amount: e.target.value })} />
</div>
</label><label>Cheque Number *<input disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} value={editor.chequeNo} onChange={(e) => setEditor({ ...editor, chequeNo: e.target.value })} />
</label><label>Bank *<select disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} value={editor.bankLedgerId} onChange={(e) => setEditor({ ...editor, bankLedgerId: e.target.value })}><option value="">Select bank</option>{banks.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
</label><label className="pdc-wide">Narration<textarea disabled={editor.voucher?.status !== undefined && editor.voucher.status !== "Pending"} maxLength={2000} rows={3} value={editor.narration} onChange={(e) => setEditor({ ...editor, narration: e.target.value })} />
</label>
</section><section className="pdc-allocation-summary"><header><div><b>Allocation Summary</b><span>{editor.allocations.length} {editor.allocations.length === 1 ? "Reference" : "References"}</span>
</div>{editor.voucher?.status !== "Cleared" && editor.voucher?.status !== "Bounced" && <button onClick={() => void showAllocations()} type="button">{editor.allocations.length ? "Edit Against References" : "[Against Ref]"} →</button>}</header><div><p><small>Party Account</small><b>{selectedParty?.name || "Not selected"}</b>
</p><p><small>PDC Total / Allocated</small><b>AED {money(amount)} / {money(allocatedAmount)}</b>
</p><p className={allocatedAmount === amount && amount > 0 ? "balanced" : ""}><small>Remaining Balance</small><b>AED {money(Math.max(0, amount - allocatedAmount))} {allocatedAmount === amount && amount > 0 ? "(Fully Allocated)" : ""}</b>
</p>
</div>
</section>
</div><footer className="cv-modal-actions"><div>{editor.mode === "edit" && editor.voucher?.status === "Pending" && <button className="cv-danger" disabled={working} onClick={() => void remove()} type="button">Delete</button>}<button className="cv-secondary" disabled={working} onClick={() => void openCreate()} type="button">Clear</button>
</div><div><button className="cv-secondary" disabled={working} onClick={() => setEditor(null)} type="button">Close</button>{editor.voucher?.status !== "Cleared" && editor.voucher?.status !== "Bounced" && <><button className="cv-secondary cv-blue-outline" disabled={working} onClick={() => void save(true)} type="button">Save & Print</button><button className="cv-primary" disabled={working} onClick={() => void save(false)} type="button">{editor.mode === "create" ? "Save PDC" : "Update PDC"}</button>
</>}</div>
</footer>
</section>
</div>}
    {allocationOpen && editor && <div className="pv-allocation-backdrop"><section className="pv-allocation-dialog pdc-allocation-dialog" role="dialog" aria-modal="true"><header><div><h3>Against Reference Allocation</h3><p>{selectedParty?.name}</p>
</div><button aria-label="Close" onClick={() => setAllocationOpen(false)} type="button">×</button>
</header><div className="pv-allocation-body">{allocationError && <p className="cu-api-error">{allocationError}</p>}<div className="pdc-allocation-target"><span>Selected {partyLabel}: <b>{selectedParty?.name}</b>
</span><span>Target PDC Amount: <b>AED {money(amount)}</b>
</span>
</div><div className="pdc-allocation-target"><label>{partyLabel} Search<input placeholder="Search all accounts..." type="search" value={accountSearch} onChange={(e) => void searchAccounts(e.target.value)} /></label><label>{partyLabel} *<select value={editor.partyLedgerId} onChange={(e) => void chooseParty(e.target.value)}><option value="">Select party account</option>{parties.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label></div><div className="pv-add-allocation"><select disabled={!editor.partyLedgerId} id="pdc-reference"><option value="">Select an open reference</option>{references.filter((reference) => !editor.allocations.some((item) => item.sourceVoucherTypeId === reference.sourceVoucherTypeId && item.sourceVoucherNo === reference.sourceVoucherNo)).map((reference) => <option key={`${reference.sourceVoucherTypeId}|${reference.sourceVoucherNo}`} value={`${reference.sourceVoucherTypeId}|${reference.sourceVoucherNo}`}>{reference.sourceInvoiceNo || reference.sourceVoucherNo} · Pending {money(reference.pendingAmount)} {reference.currencySymbol || "AED"}</option>)}</select><button className="cv-secondary" disabled={!editor.partyLedgerId} onClick={() => { const select = document.getElementById("pdc-reference") as HTMLSelectElement | null; addReference(select?.value || ""); if (select) select.value = ""; }} type="button">+ Against</button>
</div><div className="pv-allocation-table"><table><thead><tr><th>Ref Type</th><th>Source Type</th><th>Reference No.</th><th>Pending Amount</th><th>Allocation Amount</th><th>Curr</th><th />
</tr>
</thead><tbody>{editor.allocations.map((item, index) => <tr key={`${item.sourceVoucherTypeId}-${item.sourceVoucherNo}`}><td>Against</td><td>{item.sourceTypeName}</td><td>{item.sourceLabel}</td><td>{money(item.pendingAmount)}</td><td><input min="0.01" max={item.pendingAmount} step="0.01" type="number" value={item.amount} onChange={(e) => updateAllocation(index, e.target.value)} />
</td><td>{item.currencySymbol}</td><td><button aria-label="Remove allocation" onClick={() => removeAllocation(index)} type="button">×</button>
</td>
</tr>)}{!editor.allocations.length && <tr><td className="cv-empty" colSpan={7}>Choose an open reference above.</td>
</tr>}</tbody>
</table>
</div><div className="pdc-allocation-total"><span>Strict Against Allocation</span><span>Allocated: <b>AED {money(allocatedAmount)}</b>
</span>
</div>
</div><footer><span>All allocations must belong to this {partyLabel.toLowerCase()}.</span><div><button className="cv-secondary" onClick={() => setAllocationOpen(false)} type="button">Close</button><button className="cv-primary" onClick={validateAllocations} type="button">Save Allocations</button>
</div>
</footer>
</section>
</div>}
  </div>;
}

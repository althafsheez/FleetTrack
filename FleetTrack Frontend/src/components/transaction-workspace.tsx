"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FleetSidebar } from './fleet-sidebar';
import { Dialog, Picker, printDocument } from './transaction-controls';
import { ApiError, getCurrentUser, logout, request, type AuthenticatedUser } from '@/lib/api';
import { csv, dateText, money, query, titles, today, type DocumentKind, type Lookup, type Register, type Row, type TransactionDocument } from '@/lib/transactions';
import '@/app/transactions.css';

type Fields = Record<string, string>;
type Allocation = { voucherTypeId: number; voucherNo: string; amount: string };
type EditorLine = Fields & { key: string };
type Editor = { document?: TransactionDocument; fields: Fields; lines: EditorLine[]; key: string };
const emptyFilters = { fromDate: '', toDate: '', q: '', ledgerId: '', status: '', mode: '', dateBasis: 'voucher' };
const uid = () => crypto.randomUUID();
const str = (value: unknown) => value == null ? '' : String(value);
const num = (value: string | undefined) => value && Number(value) > 0 ? Number(value) : null;
const dateValue = (value: string | undefined) => value ? `${value}T00:00:00` : null;
const errorText = (error: unknown) => error instanceof Error ? error.message : 'The request could not be completed';
const newLine = (): EditorLine => ({ key: uid(), description: '', qty: '1', rate: '', direction: 'Dr', amount: '', unitId: '', taxId: '', vehicleId: '', productId: '', itemTypeId: '', ledgerId: '', exchangeRateId: '', sourceLineId: '', chequeNo: '', chequeDate: '' });

function fromDocument(doc: TransactionDocument): Editor {
  const h = doc.header;
  const fields: Fields = {
    date: str(h.date || h.docDate).slice(0, 10), manualNumber: str(h.invoiceNo || h.financeNo), ledgerId: str(h.ledgerId), exchangeRateId: str(h.exchangeRateId),
    accountId: str(h.purchaseAccount || h.salesAccount), employeeId: str(h.employeeId || ''), pricingLevelId: str(h.pricinglevelId || ''),
    dueDate: str(h.dueDate).slice(0, 10), invoiceDate: str(h.vendorInvoiceDate).slice(0, 10), vendorInvoiceNo: str(h.vendorInvoiceNo),
    creditPeriod: str(h.creditPeriod || 0), sourceId: str(h.purchaseOrderMasterId || h.salesMasterId || h.purchaseMasterId || ''),
    purchaseMode: h.isFaPurchase ? 'asset' : h.isInvPurchase ? 'inventory' : 'misc', narration: str(h.narration), discount: str(h.billDiscount || h.discount || 0),
    transportationCompany: str(h.transportationCompany), lrNo: str(h.lrNo), approved: h.approved ? 'true' : '', cancelled: h.cancelled ? 'true' : '',
    loanAmount: str(h.loanAmount), monthlyAmount: str(h.monthlyAmount), installments: str(h.NoOfInstallments || 1), bankId: str(h.bankId), assetId: str(h.assetID),
    purchaseDetailId: str(h.purchaseDetailId), chequeNoFrom: str(h.chequeNoFrom), chequeDateFrom: str(h.chequeDateFrom).slice(0, 10),
  };
  const lines = doc.lines.map(row => ({ ...newLine(), ...Object.fromEntries(Object.entries(row).map(([key, value]) => [key, str(value)])),
    description: str(row.itemDescription || row.description), sourceLineId: str(row.orderDetailsId || row.salesDetailsId || ''),
    direction: Number(row.credit) > 0 ? 'Cr' : 'Dr', amount: str(Number(row.credit) > 0 ? row.credit : row.debit || row.amount),
    chequeDate: str(row.chequeDate).slice(0, 10), key: uid() }));
  return { document: doc, fields, lines, key: uid() };
}

export function TransactionWorkspace({ kind }: { kind: DocumentKind }) {
  const router = useRouter(), title = titles[kind];
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [filters, setFilters] = useState(emptyFilters), [activeFilters, setActiveFilters] = useState(emptyFilters);
  const [page, setPage] = useState<Register>({ items: [], total: 0, offset: 0, limit: 25 });
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false);
  const [error, setError] = useState(''), [editorError, setEditorError] = useState(''), [notice, setNotice] = useState('');
  const [editor, setEditor] = useState<Editor | null>(null), [rates, setRates] = useState<Lookup[]>([]);
  const [allocations, setAllocations] = useState<Record<string, Allocation[]>>({});
  const [against, setAgainst] = useState<{ key: string; refs: Row[] } | null>(null);
  const [schedule, setSchedule] = useState<Row[]>([]);
  const [purchaseLines, setPurchaseLines] = useState<Row[]>([]);
  const [taxes, setTaxes] = useState<Lookup[]>([]);
  const [printAfterSave, setPrintAfterSave] = useState(false);
  const requestSequence = useRef(0);
  const financial = kind === 'purchase-invoices' || kind === 'credit-notes';
  const finance = kind === 'vehicle-finance', debit = kind === 'debit-notes', order = kind === 'purchase-orders', quotation = kind === 'sales-quotations';
  const locked = !!editor?.document?.header.isPosted;

  const load = useCallback(async (values = emptyFilters, offset = 0) => {
    const sequence = ++requestSequence.current;
    setLoading(true); setError('');
    try {
      const result = await request<Register>(`/transaction-documents/${kind}/page${query({ ...values, offset, limit: 25 })}`);
      if (sequence === requestSequence.current) setPage(result);
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) router.replace('/login');
      else if (sequence === requestSequence.current) setError(errorText(cause));
    } finally { if (sequence === requestSequence.current) setLoading(false); }
  }, [kind, router]);

  useEffect(() => {
    let active = true;
    getCurrentUser().then(current => { if (active) { setUser(current); void load(); } }).catch(cause => {
      if (cause instanceof ApiError && cause.status === 401) router.replace('/login');
      else setError(errorText(cause));
    });
    return () => { active = false; };
  }, [load, router]);
  const editorDate = editor?.fields.date;
  useEffect(() => {
    if (!financial) return;
    let active = true;
    request<Lookup[]>('/transaction-documents/lookups/taxes').then(rows => { if (active) setTaxes(rows); }).catch(cause => { if (active) setError(errorText(cause)); });
    return () => { active = false; };
  }, [financial]);
  useEffect(() => {
    if (!editorDate) return;
    let active = true;
    request<(Lookup & { currencyName?: string; currencySymbol?: string })[]>(`/transaction-documents/lookups/exchange-rates${query({ date: `${editorDate}T00:00:00` })}`)
      .then(rows => { if (active) setRates(rows.map(row => ({ ...row, name: row.name || `${row.currencyName || ''} ${row.currencySymbol || ''}` }))); })
      .catch(cause => { if (active) setEditorError(errorText(cause)); });
    return () => { active = false; };
  }, [editorDate]);

  function field(key: string, value: string) { setEditor(current => current ? { ...current, fields: { ...current.fields, [key]: value } } : current); }
  function lineField(key: string, name: string, value: string) {
    setEditor(current => current ? { ...current, lines: current.lines.map(line => line.key === key ? { ...line, [name]: value } : line) } : current);
    if (['ledgerId', 'direction', 'exchangeRateId'].includes(name)) setAllocations(current => ({ ...current, [key]: [] }));
  }
  function closeEditor() { if (!busy && (!editor || locked || window.confirm('Close this transaction? Unsaved changes will be lost.'))) { setEditor(null); setAgainst(null); } }
  function create() {
    setEditorError(''); setSchedule([]); setAllocations({}); setPurchaseLines([]);
    setEditor({ fields: { date: today(), dueDate: today(), invoiceDate: today(), purchaseMode: 'misc', creditPeriod: '0', discount: '0', installments: '1', chequeDateFrom: today() }, lines: [newLine()], key: uid() });
  }
  async function open(identity: number) {
    setBusy(true); setError(''); setEditorError(''); setAllocations({});
    try {
      const doc = await request<TransactionDocument>(`/transaction-documents/${kind}/${identity}`);
      restore(doc);
      if (finance && doc.header.purchaseMasterId) {
        const source = await request<{ lines: Row[] }>(`/transaction-documents/sources/purchases/${doc.header.purchaseMasterId}`);
        setPurchaseLines(source.lines);
      }
    }
    catch (cause) { setError(errorText(cause)); } finally { setBusy(false); }
  }
  function restore(doc: TransactionDocument) {
    const next = fromDocument(doc);
    setEditor(next); setSchedule(finance ? doc.lines : []);
    setAllocations(Object.fromEntries(next.lines.map(line => [line.key, (doc.allocations || [])
      .filter(row => str(row.ledgerId) === line.ledgerId)
      .map(row => ({ voucherTypeId: Number(row.voucherTypeId), voucherNo: str(row.voucherNo), amount: str(row.amount) }))])));
  }
  function payload() {
    if (!editor) throw new Error('No open transaction');
    const f = editor.fields;
    return {
      date: dateValue(f.date), manualNumber: f.manualNumber || '', ledgerId: num(f.ledgerId), exchangeRateId: num(f.exchangeRateId), accountId: num(f.accountId),
      employeeId: num(f.employeeId), pricingLevelId: num(f.pricingLevelId), dueDate: dateValue(f.dueDate), vendorInvoiceNo: f.vendorInvoiceNo || '',
      invoiceDate: dateValue(f.invoiceDate), creditPeriod: Number(f.creditPeriod || 0), sourceId: num(f.sourceId), purchaseMode: f.purchaseMode || 'misc',
      narration: f.narration || '', discount: f.discount || '0', transportationCompany: f.transportationCompany || '', lrNo: f.lrNo || '',
      approved: f.approved === 'true', cancelled: f.cancelled === 'true', loanAmount: f.loanAmount || '0', monthlyAmount: f.monthlyAmount || '0',
      installments: Number(f.installments || 1), bankId: num(f.bankId), assetId: num(f.assetId), purchaseDetailId: num(f.purchaseDetailId),
      chequeNoFrom: f.chequeNoFrom || '', chequeDateFrom: dateValue(f.chequeDateFrom), idempotencyKey: editor.key, expectedVersion: editor.document?.version || null,
      lines: finance ? [] : editor.lines.map(line => ({ id: num(line.id), description: line.description || '', vehicleId: num(line.vehicleId), unitId: num(line.unitId),
        qty: line.qty || '1', rate: line.rate || '0', taxId: num(line.taxId), productId: num(line.productId), itemTypeId: num(line.itemTypeId), sourceLineId: num(line.sourceLineId),
        ledgerId: num(line.ledgerId), direction: line.direction, amount: line.amount || '0', exchangeRateId: num(line.exchangeRateId), chequeNo: line.chequeNo || '',
        chequeDate: dateValue(line.chequeDate), allocations: allocations[line.key] || [] })),
    };
  }
  async function save() {
    if (!editor) return;
    const printWindow = printAfterSave ? window.open('', '_blank') : null;
    if (printAfterSave && !printWindow) { setEditorError('Allow pop-ups to print after saving'); return; }
    setBusy(true); setEditorError('');
    try {
      const saved = await request<TransactionDocument>(`/transaction-documents/${kind}${editor.document ? `/${editor.document.id}` : ''}`, {
        method: editor.document ? 'PATCH' : 'POST', body: JSON.stringify(payload()),
      });
      restore(saved); setNotice(`${title} saved.`);
      if (printWindow) printDocument(title, saved.header, saved.lines, printWindow);
      await load(activeFilters, page.offset);
    } catch (cause) { printWindow?.close(); setEditorError(errorText(cause)); } finally { setBusy(false); }
  }
  async function command(action: 'post' | 'unpost' | 'delete') {
    if (!editor?.document || !window.confirm(`${action === 'delete' ? 'Delete' : action === 'post' ? 'Post' : 'Unpost'} transaction ${editor.fields.manualNumber}?`)) return;
    setBusy(true); setEditorError('');
    try {
      const doc = editor.document;
      if (action === 'delete') {
        await request(`/transaction-documents/${kind}/${doc.id}${query({ expectedVersion: doc.version })}`, { method: 'DELETE' }); setEditor(null);
      } else {
        const saved = await request<TransactionDocument>(`/transaction-documents/${kind}/${doc.id}/${action}`, { method: 'POST', body: JSON.stringify({ expectedVersion: doc.version }) }); setEditor(fromDocument(saved));
      }
      setNotice('Transaction updated.'); await load(activeFilters, page.offset);
    } catch (cause) { setEditorError(errorText(cause)); } finally { setBusy(false); }
  }
  async function importSource() {
    if (!editor?.fields.sourceId) return;
    setBusy(true); setEditorError('');
    try {
      const source = finance ? 'purchases' : kind === 'credit-notes' ? 'sales' : 'purchase-orders';
      const data = await request<{ header: Row; lines: Row[] }>(`/transaction-documents/sources/${source}/${editor.fields.sourceId}`);
      if (finance) {
        setPurchaseLines(data.lines);
        const first = data.lines[0]; if (!first) throw new Error('Purchase has no asset lines');
        field('purchaseDetailId', str(first.purchaseDetailsId)); field('assetId', str(first.productId));
      } else {
        setEditor(current => current ? { ...current, fields: { ...current.fields, ledgerId: str(data.header.ledgerId), exchangeRateId: str(data.header.exchangeRateId) },
          lines: data.lines.filter(row => row.remainingQuantity == null || Number(row.remainingQuantity) > 0).map(row => ({ ...newLine(),
            sourceLineId: str(row.purchaseOrderDetailsId || row.salesDetailsId), description: str(row.itemDescription || row.description),
            qty: str(row.remainingQuantity ?? row.qty), rate: str(row.rate), unitId: str(row.unitId), vehicleId: str(row.vehicleId), itemTypeId: str(row.itemTypeId), taxId: str(row.taxId),
          })) } : current);
      }
    } catch (cause) { setEditorError(errorText(cause)); } finally { setBusy(false); }
  }
  async function showAgainst(line: EditorLine) {
    if (!line.ledgerId) { setEditorError('Select the line account first'); return; }
    try { setAgainst({ key: line.key, refs: await request<Row[]>(`/transaction-documents/references${query({ ledgerId: line.ledgerId, direction: line.direction })}`) }); }
    catch (cause) { setEditorError(errorText(cause)); }
  }
  async function previewSchedule() {
    setBusy(true); setEditorError('');
    try { setSchedule(await request<Row[]>('/transaction-documents/vehicle-finance/preview', { method: 'POST', body: JSON.stringify(payload()) })); }
    catch (cause) { setEditorError(errorText(cause)); } finally { setBusy(false); }
  }
  const statuses = order ? ['pending', 'overdue', 'cancelled'] : quotation ? ['approved', 'pending'] : debit ? [] : ['posted', 'draft'];
  const gross = editor?.lines.reduce((total, line) => total + Number(line.qty || 0) * Number(line.rate || 0), 0) || 0;
  const taxTotal = editor?.lines.reduce((total, line) => total + Number(line.qty || 0) * Number(line.rate || 0) * Number(taxes.find(tax => str(tax.id) === line.taxId)?.rate || 0) / 100, 0) || 0;
  const sumDirection = (direction: string) => editor?.lines.filter(line => line.direction === direction).reduce((total, line) => total + Number(line.amount || 0), 0) || 0;
  function input(key: string, label: string, type = 'text') {
    return <label key={key}>{label}<input type={type} value={editor?.fields[key] || ''} disabled={locked || busy} min={type === 'number' ? '0' : undefined} step={type === 'number' ? 'any' : undefined} onChange={event => field(key, event.target.value)} /></label>;
  }
  function picker(key: string, label: string, name: string) {
    return <label key={key}>{label}<Picker label={label} name={name} value={editor?.fields[key] || ''} disabled={locked || busy} onChange={value => field(key, value)} /></label>;
  }
  function rateSelect(value: string, update: (value: string) => void) {
    return <select aria-label="Currency" value={value} disabled={locked || busy} onChange={event => update(event.target.value)}><option value="">Select currency</option>{rates.map(rate => <option key={rate.id} value={rate.id}>{rate.name}</option>)}</select>;
  }
  if (!user) return <main className="ft-loading">{error || 'Loading transactions...'}</main>;
  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><strong>{title}</strong></div><div className="cu-user"><span>{user.displayName}</span><button className="cu-logout" onClick={() => void logout().finally(() => router.replace('/login'))}>Logout</button></div></header>
    <main className="tx-workspace"><div className="tx-heading"><div><h1>{title}</h1><p>{page.total} records</p></div><div className="tx-actions"><button disabled={!page.items.length} onClick={() => csv(page.items, kind)} title="Export current page as CSV">Export Page</button><button className="tx-primary" onClick={create}>New Transaction</button></div></div>
      {error && <div className="tx-error" role="alert">{error}</div>}{notice && <div className="tx-notice" role="status">{notice}</div>}
      <form className="tx-filters" onSubmit={event => { event.preventDefault(); setActiveFilters(filters); void load(filters); }}>
        <label>From date<input type="date" value={filters.fromDate} onChange={e => setFilters({ ...filters, fromDate: e.target.value })} /></label>
        <label>To date<input type="date" value={filters.toDate} onChange={e => setFilters({ ...filters, toDate: e.target.value })} /></label>
        <label>Number<input value={filters.q} onChange={e => setFilters({ ...filters, q: e.target.value })} /></label>
        {!debit && <label>Party<Picker name="accounts" label="Party" value={filters.ledgerId} onChange={value => setFilters({ ...filters, ledgerId: value })} /></label>}
        {!!statuses.length && <label>Status<select value={filters.status} onChange={e => setFilters({ ...filters, status: e.target.value })}><option value="">All</option>{statuses.map(status => <option key={status} value={status}>{status[0].toUpperCase() + status.slice(1)}</option>)}</select></label>}
        {kind === 'purchase-invoices' && <><label>Date basis<select value={filters.dateBasis} onChange={e => setFilters({ ...filters, dateBasis: e.target.value })}><option value="voucher">Voucher date</option><option value="invoice">Invoice date</option></select></label><label>Purchase mode<select value={filters.mode} onChange={e => setFilters({ ...filters, mode: e.target.value })}><option value="">All</option><option value="misc">Miscellaneous</option><option value="asset">Fixed asset</option><option value="inventory">Inventory</option></select></label></>}
        <button className="tx-primary" disabled={loading}>Search</button><button type="button" disabled={loading} onClick={() => { setFilters(emptyFilters); setActiveFilters(emptyFilters); void load(); }}>Reset</button>
      </form>
      <div className="tx-table-wrap"><table className="tx-table"><thead><tr><th>Number</th><th>Date</th><th>{finance ? 'Financing party' : 'Party'}</th><th>Status</th><th>Narration</th><th className="tx-amount">Amount</th><th /></tr></thead><tbody>
        {loading ? <tr><td className="tx-empty" colSpan={7}>Loading...</td></tr> : !page.items.length ? <tr><td className="tx-empty" colSpan={7}>No matching transactions</td></tr> : page.items.map(row => <tr key={str(row.id)}>
          <td><button onClick={() => void open(Number(row.id))} disabled={busy}>{str(row.number)}</button></td><td>{dateText(row.documentDate)}</td><td>{str(row.partyName) || '-'}</td>
          <td><span className={`tx-status ${row.isPosted ? 'tx-status-posted' : ''}`}>{order ? row.cancelled ? 'Cancelled' : 'Open' : quotation ? row.approved ? 'Approved' : 'Pending' : debit ? 'Recorded' : row.isPosted ? 'Posted' : 'Draft'}</span></td>
          <td>{str(row.narration) || '-'}</td><td className="tx-amount">{money(row.grandTotal ?? row.loanAmount ?? row.totalAmount)}</td><td><button disabled={busy} onClick={() => void open(Number(row.id))}>View Details</button></td>
        </tr>)}
      </tbody></table></div><footer className="tx-pagination"><span>{page.total ? page.offset + 1 : 0}-{Math.min(page.offset + page.limit, page.total)} of {page.total}</span><div className="tx-actions"><button disabled={!page.offset || loading} onClick={() => void load(activeFilters, Math.max(0, page.offset - 25))}>Previous</button><button disabled={page.offset + page.limit >= page.total || loading} onClick={() => void load(activeFilters, page.offset + 25)}>Next</button></div></footer>
    </main>
    {editor && <Dialog title={`${editor.document ? editor.fields.manualNumber : 'New'} - ${title}`} onClose={closeEditor}>
      <div className="tx-editor-body">{editorError && <div className="tx-error" role="alert">{editorError}</div>}
        <div className="tx-fields">
          {finance ? input('manualNumber', 'Finance number') : <label>Voucher number<input value={editor.document ? editor.fields.manualNumber : 'Automatic on save'} disabled /></label>}
          {input('date', 'Voucher date', 'date')}
          {!debit && picker('ledgerId', finance ? 'Financing party' : order || kind === 'purchase-invoices' ? 'Supplier' : 'Customer', 'accounts')}
          {!debit && !finance && <label>Currency{rateSelect(editor.fields.exchangeRateId || '', value => field('exchangeRateId', value))}</label>}
          {order && input('dueDate', 'Due date', 'date')}
          {order && <label>Due days<input type="number" min="0" step="1" disabled={locked || busy} value={Math.max(0, Math.round((Date.parse(editor.fields.dueDate || editor.fields.date) - Date.parse(editor.fields.date)) / 86400000)) || 0} onChange={e => { const days = Number(e.target.value); if (Number.isInteger(days) && days >= 0 && editor.fields.date) field('dueDate', new Date(Date.parse(editor.fields.date) + days * 86400000).toISOString().slice(0, 10)); }} /></label>}
          {quotation && <>{picker('employeeId', 'Salesperson', 'employees')}{picker('pricingLevelId', 'Pricing level', 'pricing')}</>}
          {financial && <>{picker('accountId', kind === 'purchase-invoices' ? 'Purchase account' : 'Sales account', 'accounts')}{kind === 'credit-notes' && picker('employeeId', 'Salesperson', 'employees')}</>}
          {kind === 'purchase-invoices' && <>{input('vendorInvoiceNo', 'Vendor invoice number')}{input('invoiceDate', 'Invoice date', 'date')}{input('creditPeriod', 'Credit period (days)', 'number')}<label>Purchase mode<select disabled={locked || busy} value={editor.fields.purchaseMode} onChange={e => field('purchaseMode', e.target.value)}><option value="misc">Miscellaneous purchase</option><option value="asset">Fixed asset purchase</option><option value="inventory">Inventory purchase</option></select></label></>}
          {(financial || finance) && <>{picker('sourceId', finance ? 'Purchase invoice' : kind === 'credit-notes' ? 'Source invoice' : 'Purchase order', finance ? 'purchases' : kind === 'credit-notes' ? 'sales' : 'orders')}<div className="tx-actions"><button disabled={locked || busy || !editor.fields.sourceId} onClick={() => void importSource()}>Load Source</button></div></>}
          {finance && <><label>Purchased asset<select disabled={locked || busy} value={editor.fields.purchaseDetailId || ''} onChange={e => { const line = purchaseLines.find(row => str(row.purchaseDetailsId) === e.target.value); field('purchaseDetailId', e.target.value); field('assetId', str(line?.productId)); }}><option value="">Select asset</option>{purchaseLines.map(row => <option key={str(row.purchaseDetailsId)} value={str(row.purchaseDetailsId)}>{str(row.description)} - {money(row.amount)}</option>)}</select></label>{input('loanAmount', 'Loan amount', 'number')}{input('monthlyAmount', 'Monthly amount', 'number')}{input('installments', 'Number of installments', 'number')}{picker('bankId', 'Bank', 'accounts')}{input('chequeNoFrom', 'First cheque number')}{input('chequeDateFrom', 'First cheque date', 'date')}</>}
        </div>
        {finance ? <><div className="tx-actions"><button disabled={locked || busy} onClick={() => void previewSchedule()}>Generate Schedule</button></div><div className="tx-table-wrap"><table className="tx-table"><thead><tr><th>#</th><th>Bank</th><th>Cheque no.</th><th>Cheque date</th><th className="tx-amount">EMI amount</th><th>Paid</th></tr></thead><tbody>{schedule.map((row, index) => <tr key={index}><td>{str(row.EMIno)}</td><td>{str(row.bankId)}</td><td>{str(row.chequeNo)}</td><td>{dateText(row.EMIDate)}</td><td className="tx-amount">{money(row.EMIamount)}</td><td>{row.isPaid ? 'Yes' : 'No'}</td></tr>)}</tbody></table></div></> :
          <><div className="tx-table-wrap"><table className="tx-table tx-line-table"><thead><tr><th>#</th>{debit ? <><th>Account ledger</th><th>Dr / Cr</th><th>Against</th><th>Amount</th><th>Currency</th><th>Cheque no.</th><th>Cheque date</th></> : <>{financial && <th>Item</th>}<th>Description</th>{!quotation && <th>Vehicle</th>}<th>Quantity</th><th>Unit</th><th>Rate</th>{financial && <th>Tax</th>}<th className="tx-amount">Gross value</th></>}<th /></tr></thead><tbody>
            {editor.lines.map((line, index) => <tr key={line.key}><td>{index + 1}</td>{debit ? <>
              <td><Picker name="accounts" label="Account ledger" value={line.ledgerId} disabled={locked || busy} onChange={value => lineField(line.key, 'ledgerId', value)} /></td>
              <td><select aria-label={`Line ${index + 1} debit or credit`} value={line.direction} disabled={locked || busy} onChange={e => lineField(line.key, 'direction', e.target.value)}><option>Dr</option><option>Cr</option></select></td>
              <td><button disabled={locked || busy} onClick={() => void showAgainst(line)}>Against{allocations[line.key]?.length ? ` (${allocations[line.key].length})` : ''}</button></td>
              <td><input aria-label={`Line ${index + 1} amount`} type="number" min="0" step="0.01" value={line.amount} disabled={locked || busy} onChange={e => lineField(line.key, 'amount', e.target.value)} /></td>
              <td>{rateSelect(line.exchangeRateId, value => lineField(line.key, 'exchangeRateId', value))}</td>
              <td><input aria-label={`Line ${index + 1} cheque number`} value={line.chequeNo} disabled={locked || busy} onChange={e => lineField(line.key, 'chequeNo', e.target.value)} /></td>
              <td><input aria-label={`Line ${index + 1} cheque date`} type="date" value={line.chequeDate} disabled={locked || busy} onChange={e => lineField(line.key, 'chequeDate', e.target.value)} /></td>
            </> : <>
              {financial && <td><Picker name={kind === 'credit-notes' ? 'item-types' : editor.fields.purchaseMode === 'asset' ? 'assets' : 'products'} label="Item" value={kind === 'credit-notes' ? line.itemTypeId : line.productId} disabled={locked || busy} onChange={value => lineField(line.key, kind === 'credit-notes' ? 'itemTypeId' : 'productId', value)} /></td>}
              <td className="tx-description"><input aria-label={`Line ${index + 1} description`} value={line.description} disabled={locked || busy} onChange={e => lineField(line.key, 'description', e.target.value)} /></td>
              {!quotation && <td><Picker name="vehicles" label="Vehicle" value={line.vehicleId} disabled={locked || busy} onChange={value => lineField(line.key, 'vehicleId', value)} /></td>}
              <td><input aria-label={`Line ${index + 1} quantity`} type="number" min="0.00001" step="any" value={line.qty} disabled={locked || busy} onChange={e => lineField(line.key, 'qty', e.target.value)} /></td>
              <td><Picker name="units" label="Unit" value={line.unitId} disabled={locked || busy} onChange={value => lineField(line.key, 'unitId', value)} /></td>
              <td><input aria-label={`Line ${index + 1} rate`} type="number" min="0" step="any" value={line.rate} disabled={locked || busy} onChange={e => lineField(line.key, 'rate', e.target.value)} /></td>
              {financial && <td><Picker name="taxes" label="Tax" value={line.taxId} disabled={locked || busy} onChange={value => lineField(line.key, 'taxId', value)} /></td>}
              <td className="tx-amount">{money(Number(line.qty || 0) * Number(line.rate || 0))}</td>
            </>}<td className="tx-remove"><button title="Remove line" aria-label={`Remove line ${index + 1}`} disabled={locked || busy} onClick={() => setEditor({ ...editor, lines: editor.lines.length === 1 ? [newLine()] : editor.lines.filter(item => item.key !== line.key) })}>×</button></td></tr>)}
          </tbody></table></div><div className="tx-actions" style={{ marginTop: 10 }}><button disabled={locked || busy || editor.lines.length >= 200} onClick={() => setEditor({ ...editor, lines: [...editor.lines, newLine()] })}>Add Line</button></div></>}
        {debit ? <div className="tx-totals"><div>Debit<strong>{money(sumDirection('Dr'))}</strong></div><div>Credit<strong>{money(sumDirection('Cr'))}</strong></div><div>Difference<strong>{money(sumDirection('Dr') - sumDirection('Cr'))}</strong></div></div> : !finance && <div className="tx-totals"><div>Gross total<strong>{money(gross)}</strong></div>{financial && <><div>Tax<strong>{money(taxTotal)}</strong></div><div>Grand total<strong>{money(gross + taxTotal - Number(editor.fields.discount || 0))}</strong></div></>}</div>}
        <div className="tx-fields">{financial && input('discount', 'Bill discount', 'number')}{kind === 'purchase-invoices' && <>{input('transportationCompany', 'Transportation company')}{input('lrNo', 'LR number')}</>}
          {order && <label className="tx-check"><input type="checkbox" disabled={locked || busy} checked={editor.fields.cancelled === 'true'} onChange={e => field('cancelled', e.target.checked ? 'true' : '')} />Cancelled</label>}
          {quotation && <label className="tx-check"><input type="checkbox" disabled={locked || busy} checked={editor.fields.approved === 'true'} onChange={e => field('approved', e.target.checked ? 'true' : '')} />Approved</label>}
        </div><label>Narration<textarea value={editor.fields.narration || ''} disabled={locked || busy} onChange={e => field('narration', e.target.value)} /></label>
      </div>
      <footer className="tx-footer"><div className="tx-actions">{editor.document && <><button className="tx-danger" disabled={locked || busy} onClick={() => void command('delete')}>Delete</button><button disabled={busy} onClick={() => { if (editor.document) printDocument(title, editor.document.header, editor.document.lines); }}>Print</button></>}</div><div className="tx-actions">
        {editor.document && (financial || finance) && <button disabled={busy || (finance && locked) || kind === 'credit-notes'} title={kind === 'credit-notes' ? 'Posting awaits verification of legacy accounting rules' : undefined} onClick={() => void command(locked ? 'unpost' : 'post')}>{locked ? 'Unpost' : 'Post'}</button>}
        <label className="tx-check"><input type="checkbox" checked={printAfterSave} onChange={e => setPrintAfterSave(e.target.checked)} />Print after save</label>
        <button disabled={busy} onClick={() => { if (window.confirm('Clear the form and start a new transaction?')) create(); }}>Clear</button>
        <button disabled={busy} onClick={closeEditor}>Close</button><button className="tx-primary" disabled={locked || busy} onClick={() => void save()}>{busy ? 'Working...' : editor.document ? 'Save Changes' : 'Save'}</button>
      </div></footer>
    </Dialog>}
    {against && <Dialog title="Against References" onClose={() => setAgainst(null)}><div className="tx-editor-body"><table className="tx-table"><thead><tr><th>Reference</th><th>Pending</th><th>Allocate</th></tr></thead><tbody>{against.refs.map(ref => {
      const values = allocations[against.key] || [], value = values.find(item => item.voucherTypeId === Number(ref.voucherTypeId) && item.voucherNo === str(ref.voucherNo));
      return <tr key={`${ref.voucherTypeId}:${ref.voucherNo}`}><td>{str(ref.invoiceNo || ref.voucherNo)}</td><td>{money(ref.pendingAmount)}</td><td><input aria-label={`Allocate ${ref.invoiceNo}`} type="number" min="0" max={str(ref.pendingAmount)} step="0.01" value={value?.amount || ''} onChange={e => { const next = values.filter(item => !(item.voucherTypeId === Number(ref.voucherTypeId) && item.voucherNo === str(ref.voucherNo))); if (Number(e.target.value) > 0) next.push({ voucherTypeId: Number(ref.voucherTypeId), voucherNo: str(ref.voucherNo), amount: e.target.value }); setAllocations({ ...allocations, [against.key]: next }); }} /></td></tr>;
    })}{!against.refs.length && <tr><td colSpan={3}>No open references</td></tr>}</tbody></table></div><footer className="tx-footer"><button className="tx-primary" onClick={() => setAgainst(null)}>Done</button></footer></Dialog>}
  </div></div>;
}

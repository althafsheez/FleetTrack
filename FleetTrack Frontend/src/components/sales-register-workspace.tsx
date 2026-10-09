"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FleetSidebar } from './fleet-sidebar';
import { Dialog, Picker, printDocument } from './transaction-controls';
import { ApiError, getCurrentUser, request, type AuthenticatedUser } from '@/lib/api';
import { csv, dateText, money, query, type Register, type Row } from '@/lib/transactions';
import '@/app/transactions.css';

const defaults = { fromDate: '', toDate: '', invoiceNo: '', ledgerId: '', voucherTypeId: '', contractId: '', fineNo: '', location: '', posted: '' };
const str = (value: unknown) => value == null ? '' : String(value);
const failure = (error: unknown) => error instanceof Error ? error.message : 'Request failed';
const displayLines = (lines: Row[]) => lines.map(row => ({ Description: row.description, Quantity: row.qty, Rate: row.rate, Tax: row.taxAmount, Amount: row.amount }));

export function SalesRegisterWorkspace() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [filters, setFilters] = useState(defaults), [active, setActive] = useState(defaults);
  const [page, setPage] = useState<Register>({ items: [], total: 0, offset: 0, limit: 25 });
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false), [error, setError] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [detail, setDetail] = useState<{ header: Row; lines: Row[] } | null>(null);
  const [salik, setSalik] = useState<Row[] | null>(null);
  const [exportFormat, setExportFormat] = useState('excel');
  const sequence = useRef(0);
  const load = useCallback(async (values = defaults, offset = 0) => {
    const id = ++sequence.current;
    setLoading(true); setError('');
    try {
      const result = await request<Register>(`/transaction-documents/sales-register/page${query({ ...values, offset, limit: 25 })}`);
      if (id === sequence.current) { setPage(result); setSelected([]); }
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) router.replace('/login');
      else if (id === sequence.current) setError(failure(cause));
    } finally { if (id === sequence.current) setLoading(false); }
  }, [router]);
  useEffect(() => {
    let active = true;
    getCurrentUser().then(value => { if (active) { setUser(value); void load(); } }).catch(cause => {
      if (cause instanceof ApiError && cause.status === 401) router.replace('/login'); else setError(failure(cause));
    });
    return () => { active = false; };
  }, [router, load]);
  async function open(id: string) {
    setBusy(true); setError('');
    try { setDetail(await request(`/transaction-documents/sales-register/${id}`)); setSalik(null); }
    catch (cause) { setError(failure(cause)); } finally { setBusy(false); }
  }
  async function loadSalik() {
    if (!detail) return;
    setBusy(true); setError('');
    try { setSalik(await request(`/transaction-documents/sales-register/${detail.header.id}/salik`)); }
    catch (cause) { setError(failure(cause)); } finally { setBusy(false); }
  }
  function print(title: string, header: Row, lines: Row[]) {
    try { printDocument(title, header, lines); } catch (cause) { setError(failure(cause)); }
  }
  async function exportInvoices() {
    setBusy(true); setError('');
    try {
      const values = Object.fromEntries(Object.entries(active).filter(([, value]) => value !== ''));
      const response = await fetch('/api/transaction-documents/sales-register/export', { method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...values, format: exportFormat, identities: selected.map(Number) }) });
      if (!response.ok) { const body = await response.json(); throw new Error(typeof body.detail === 'string' ? body.detail : 'Export failed'); }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement('a'); link.href = url; link.download = `sales-invoices.${exportFormat === 'pdf' ? 'pdf' : 'xml'}`; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (cause) { setError(failure(cause)); } finally { setBusy(false); }
  }
  const selectedRows = page.items.filter(row => selected.includes(str(row.id)));
  if (!user) return <main className="ft-loading">{error || 'Loading invoices...'}</main>;
  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><strong>Sales Invoice Register</strong></div><div className="cu-user">{user.displayName}</div></header>
    <main className="tx-workspace"><div className="tx-heading"><div><h1>Sales Invoice Register</h1><p>{page.total} records</p></div><div className="tx-actions">
      <select aria-label="Export format" value={exportFormat} onChange={e => setExportFormat(e.target.value)}><option value="excel">Excel XML</option><option value="pdf">PDF</option></select>
      <button disabled={!page.items.length || loading || busy} onClick={() => void exportInvoices()}>{selected.length ? 'Export Selected' : 'Export Filtered'}</button>
      <button disabled={!page.items.length || loading} onClick={() => csv(selected.length ? selectedRows : page.items, 'sales-invoice-register')}>CSV</button>
      <button disabled={!selected.length} onClick={() => print('Sales Invoice Register', {}, selectedRows)}>Print Selected</button>
    </div></div>
      {error && !detail && <div className="tx-error" role="alert">{error}</div>}
      <form className="tx-filters" onSubmit={e => { e.preventDefault(); setActive(filters); void load(filters); }}>
        {([['fromDate', 'From date', 'date'], ['toDate', 'To date', 'date'], ['invoiceNo', 'Invoice number', 'text'], ['fineNo', 'Fine number', 'text'], ['location', 'Location', 'text']] as const).map(([key, label, type]) => <label key={key}>{label}<input type={type} value={filters[key]} onChange={e => setFilters({ ...filters, [key]: e.target.value })} /></label>)}
        {([['ledgerId', 'Customer', 'accounts'], ['voucherTypeId', 'Voucher type', 'sales-voucher-types'], ['contractId', 'Contract', 'contracts']] as const).map(([key, label, name]) => <label key={key}>{label}<Picker label={label} name={name} value={filters[key]} onChange={value => setFilters({ ...filters, [key]: value })} /></label>)}
        <label>Status<select value={filters.posted} onChange={e => setFilters({ ...filters, posted: e.target.value })}><option value="">All</option><option value="true">Posted</option><option value="false">Not posted</option></select></label>
        <button className="tx-primary" disabled={loading}>Search</button><button type="button" disabled={loading} onClick={() => { setFilters(defaults); setActive(defaults); void load(); }}>Reset</button>
      </form>
      <div className="tx-table-wrap"><table className="tx-table"><thead><tr><th><input aria-label="Select page" type="checkbox" checked={!!page.items.length && selected.length === page.items.length} onChange={e => setSelected(e.target.checked ? page.items.map(row => str(row.id)) : [])} /></th><th>Invoice</th><th>Type</th><th>Date</th><th>Customer</th><th>Amount</th><th>Tax</th><th>Salesperson</th><th>LPO</th><th>Narration</th><th>Vehicle</th><th>Status</th></tr></thead><tbody>
        {loading ? <tr><td colSpan={12} className="tx-empty">Loading...</td></tr> : page.items.map(row => <tr key={str(row.id)}><td><input type="checkbox" aria-label={`Select ${row.invoiceNo}`} checked={selected.includes(str(row.id))} onChange={e => setSelected(e.target.checked ? [...selected, str(row.id)] : selected.filter(id => id !== str(row.id)))} /></td><td><button disabled={busy} onClick={() => void open(str(row.id))}>{str(row.invoiceNo)}</button></td><td>{str(row.voucherTypeName)}</td><td>{dateText(row.date)}</td><td>{str(row.customer)}</td><td className="tx-amount">{money(row.grandTotal)}</td><td className="tx-amount">{money(row.taxAmount)}</td><td>{str(row.salesperson)}</td><td>{str(row.lpoNo)}</td><td>{str(row.narration)}</td><td>{str(row.vehicleNos)}</td><td>{row.isPosted ? 'Posted' : 'Not posted'}</td></tr>)}
        {!loading && !page.items.length && <tr><td colSpan={12} className="tx-empty">No matching invoices</td></tr>}
      </tbody></table></div>
      <footer className="tx-pagination"><span>{page.total ? page.offset + 1 : 0}-{Math.min(page.offset + page.limit, page.total)} of {page.total}</span><div className="tx-actions"><button disabled={!page.offset || loading} onClick={() => void load(active, Math.max(0, page.offset - 25))}>Previous</button><button disabled={loading || page.offset + page.limit >= page.total} onClick={() => void load(active, page.offset + 25)}>Next</button></div></footer>
    </main>
    {detail && <Dialog title={str(detail.header.invoiceNo)} onClose={() => { setDetail(null); setError(''); }}><div className="tx-editor-body">
      {error && <div className="tx-error" role="alert">{error}</div>}
      <div className="tx-fields"><label>Customer<strong>{str(detail.header.customer)}</strong></label><label>Date<strong>{dateText(detail.header.date)}</strong></label><label>Amount<strong>{money(detail.header.grandTotal)}</strong></label></div>
      <p>{str(detail.header.narration)}</p>
      <div className="tx-table-wrap"><table className="tx-table"><thead><tr>{Object.keys(displayLines(detail.lines)[0] || {}).map(key => <th key={key}>{key}</th>)}</tr></thead><tbody>{displayLines(detail.lines).map((row, index) => <tr key={index}>{Object.entries(row).map(([key, value]) => <td key={key}>{key === 'Description' ? str(value) : money(value)}</td>)}</tr>)}</tbody></table></div>
      {salik && <><h3 className="tx-subheading">Salik Details</h3><div className="tx-table-wrap"><table className="tx-table"><thead><tr><th>Date and time</th><th>Vehicle</th><th>Location</th><th>Direction</th><th>Toll</th><th>With administration charge</th></tr></thead><tbody>{salik.map(row => <tr key={str(row.transaction)}><td>{str(row.date).replace('T', ' ')}</td><td>{str(row.vehicle)}</td><td>{str(row.location)}</td><td>{str(row.direction)}</td><td>{money(row.tollAmount)}</td><td>{money(row.amount)}</td></tr>)}{!salik.length && <tr><td colSpan={6}>No linked tolls</td></tr>}</tbody></table></div></>}
    </div><footer className="tx-footer"><div className="tx-actions"><button disabled={busy} onClick={() => void loadSalik()}>Salik Details</button><button onClick={() => print('Sales Invoice', detail.header, displayLines(detail.lines))}>Print Invoice</button>{!!salik?.length && <button onClick={() => print('Salik Details', { invoice: detail.header.invoiceNo }, salik)}>Print Salik</button>}</div><button onClick={() => setDetail(null)}>Close</button></footer></Dialog>}
  </div></div>;
}

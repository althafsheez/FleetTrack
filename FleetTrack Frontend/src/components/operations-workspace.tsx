"use client";

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FleetSidebar } from './fleet-sidebar';
import { Dialog, Picker, printDocument } from './transaction-controls';
import { ApiError, getCurrentUser, logout, request, type AuthenticatedUser } from '@/lib/api';
import { csv, dateText, money, query, today, type Lookup, type Register } from '@/lib/transactions';
import '@/app/transactions.css';

const str = (value: unknown) => value == null ? '' : String(value);
const failure = (error: unknown) => error instanceof Error ? error.message : 'Request failed';

export function OperationsWorkspace({ kind }: { kind: 'bank-reconciliations' | 'traffic-fines' }) {
  const bank = kind === 'bank-reconciliations', title = bank ? 'Bank Reconciliation' : 'Traffic Fines';
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null), [lookups, setLookups] = useState<Lookup[]>([]);
  const [filters, setFilters] = useState({ fromDate: `${today().slice(0, 4)}-01-01`, toDate: today(), bankLedgerId: '', status: bank ? 'unreconciled' : '', q: '' });
  const [active, setActive] = useState(filters), [page, setPage] = useState<Register>({ items: [], total: 0, offset: 0, limit: 25 });
  const [changes, setChanges] = useState<Record<string, string>>({}), [bankBalance, setBankBalance] = useState('');
  const [error, setError] = useState(''), [notice, setNotice] = useState(''), [busy, setBusy] = useState(false);
  const [fine, setFine] = useState<Record<string, string> | null>(null), [fineError, setFineError] = useState('');
  const sequence = useRef(0);
  useEffect(() => {
    let active = true;
    Promise.all([getCurrentUser(), request<Lookup[]>(bank ? '/bank-reconciliations/accounts' : '/traffic-fines/traffic-files')]).then(([current, rows]) => {
      if (active) { setUser(current); setLookups(rows); }
    }).catch(cause => { if (cause instanceof ApiError && cause.status === 401) router.replace('/login'); else setError(failure(cause)); });
    return () => { active = false; };
  }, [bank, router]);
  async function search(values = filters, offset = 0, discard = false) {
    if (!discard && Object.keys(changes).length && !window.confirm('Discard unsaved statement dates?')) return;
    if (bank && !values.bankLedgerId) { setError('Select a bank account'); return; }
    const id = ++sequence.current;
    setBusy(true); setError('');
    try {
      const result = await request<Register>(`/${kind}/page${query({ fromDate: values.fromDate, toDate: values.toDate, offset, limit: bank ? 100 : 25,
        ...(bank ? { bankLedgerId: values.bankLedgerId, status: values.status } : { q: values.q, posted: values.status === '' ? null : values.status === 'posted' }) })}`);
      if (id === sequence.current) { setPage(result); setActive(values); setChanges({}); }
    } catch (cause) { if (id === sequence.current) setError(failure(cause)); } finally { if (id === sequence.current) setBusy(false); }
  }
  async function saveReconciliation() {
    setBusy(true); setError('');
    try {
      const lines = Object.entries(changes).map(([id, value]) => ({ ledgerPostingId: Number(id), statementDate: value ? `${value}T00:00:00` : null,
        expectedStatementDate: page.items.find(row => str(row.ledgerPostingId) === id)?.statementDate || null }));
      await request('/bank-reconciliations', { method: 'PUT', body: JSON.stringify({ bankLedgerId: Number(active.bankLedgerId), lines }) });
      setNotice('Statement dates saved.'); await search(active, page.offset, true);
    } catch (cause) { setError(failure(cause)); } finally { setBusy(false); }
  }
  async function saveFine() {
    if (!fine) return;
    setBusy(true); setFineError('');
    try {
      await request('/traffic-fines', { method: 'POST', body: JSON.stringify({ ...fine, vehicleId: Number(fine.vehicleId), amount: fine.amount || '0',
        blackPoints: Number(fine.blackPoints || 0), acknowledgment: fine.acknowledgment || '0', fineDate: fine.fineDate ? `${fine.fineDate}:00` : null }) });
      setFine(null); setNotice('Traffic fine added.'); await search(active, 0, true);
    } catch (cause) { setFineError(failure(cause)); } finally { setBusy(false); }
  }
  function field(key: string, label: string, type = 'text') {
    return <label>{label}<input type={type} value={fine?.[key] || ''} min={type === 'number' ? '0' : undefined} step={type === 'number' ? 'any' : undefined} onChange={event => setFine(current => current ? { ...current, [key]: event.target.value } : current)} /></label>;
  }
  const book = Number(page.bookBalance || 0), statement = Number(bankBalance || 0);
  if (!user) return <main className="ft-loading">{error || 'Loading...'}</main>;
  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><strong>{title}</strong></div><div className="cu-user"><span>{user.displayName}</span><button className="cu-logout" onClick={() => void logout().finally(() => router.replace('/login'))}>Logout</button></div></header>
    <main className="tx-workspace"><div className="tx-heading"><h1>{title}</h1><div className="tx-actions"><button disabled={!page.items.length} onClick={() => csv(page.items, kind)}>Export Page</button>{!bank && <button className="tx-primary" onClick={() => { setFineError(''); setFine({ ticketNo: '', trafficFile: '', fineDate: `${today()}T09:00`, authority: '', vehicleId: '', amount: '', blackPoints: '0', description: '', acknowledgment: '0' }); }}>Add Traffic Fine</button>}</div></div>
      {error && <div className="tx-error" role="alert">{error}</div>}{notice && <div className="tx-notice" role="status">{notice}</div>}
      <form className="tx-filters" onSubmit={event => { event.preventDefault(); void search(); }}>
        {bank && <label>Bank account<select value={filters.bankLedgerId} onChange={e => setFilters({ ...filters, bankLedgerId: e.target.value })}><option value="">Select bank</option>{lookups.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}</select></label>}
        <label>From date<input type="date" value={filters.fromDate} onChange={e => setFilters({ ...filters, fromDate: e.target.value })} /></label>
        <label>To date<input type="date" value={filters.toDate} onChange={e => setFilters({ ...filters, toDate: e.target.value })} /></label>
        <label>Status<select value={filters.status} onChange={e => setFilters({ ...filters, status: e.target.value })}>{bank ? <><option value="unreconciled">Unreconciled</option><option value="reconciled">Reconciled</option><option value="all">All</option></> : <><option value="">All</option><option value="draft">Unbilled</option><option value="posted">Billed</option></>}</select></label>
        {!bank && <label>Ticket no.<input value={filters.q} onChange={e => setFilters({ ...filters, q: e.target.value })} /></label>}
        <button className="tx-primary" disabled={busy}>Search</button>
      </form>
      <div className="tx-table-wrap"><table className="tx-table"><thead><tr>{(bank ? ['Date', 'Voucher type', 'Voucher no.', 'Cheque no.', 'Cheque date', 'Deposit', 'Withdrawal', 'Statement date'] : ['Ticket no.', 'Fine date', 'Vehicle', 'Authority', 'Amount', 'Black points', 'Billed', 'Paid', '']).map((label, index) => <th key={index}>{label}</th>)}</tr></thead><tbody>
        {!page.items.length && <tr><td colSpan={bank ? 8 : 9} className="tx-empty">{busy ? 'Loading...' : bank && !active.bankLedgerId ? 'Select a bank and search' : 'No matching records'}</td></tr>}
        {page.items.map(row => bank ? <tr key={str(row.ledgerPostingId)}><td>{dateText(row.date)}</td><td>{str(row.voucherTypeName)}</td><td>{str(row.voucherNo)}</td><td>{str(row.chequeNo)}</td><td>{dateText(row.chequeDate)}</td><td className="tx-amount">{money(row.deposit)}</td><td className="tx-amount">{money(row.withdrawal)}</td><td><input aria-label={`Statement date for ${row.voucherNo}`} type="date" disabled={busy} value={changes[str(row.ledgerPostingId)] ?? str(row.statementDate).slice(0, 10)} onChange={e => {
          const next = { ...changes }; if (e.target.value === str(row.statementDate).slice(0, 10)) delete next[str(row.ledgerPostingId)]; else next[str(row.ledgerPostingId)] = e.target.value; setChanges(next);
        }} /></td></tr> : <tr key={str(row.ticketNo)}><td>{str(row.ticketNo)}</td><td>{dateText(row.fineDate)}</td><td>{str(row.vehicle)}</td><td>{str(row.authority)}</td><td className="tx-amount">{money(row.amount)}</td><td>{str(row.blackPoints)}</td><td>{row.isPosted ? 'Yes' : 'No'}</td><td>{row.isPaid ? 'Yes' : 'No'}</td><td><button onClick={() => printDocument('Traffic Fine', row, [])}>Print</button></td></tr>)}
      </tbody></table></div>
      <div className="tx-pagination"><span>{page.total ? page.offset + 1 : 0}-{Math.min(page.offset + page.limit, page.total)} of {page.total}</span><div className="tx-actions"><button disabled={busy || !page.offset} onClick={() => void search(active, Math.max(0, page.offset - page.limit))}>Previous</button><button disabled={busy || page.offset + page.limit >= page.total} onClick={() => void search(active, page.offset + page.limit)}>Next</button></div></div>
      {bank && <><div className="tx-balance-grid"><label>Company book balance (Dr positive)<strong>{money(book)}</strong></label><label>Bank statement balance (Dr positive)<input type="number" step="0.01" value={bankBalance} onChange={e => setBankBalance(e.target.value)} /></label><label>Difference<strong>{bankBalance ? money(book - statement) : '-'}</strong></label></div><div className="tx-actions" style={{ justifyContent: 'flex-end', marginTop: 20 }}><button disabled={busy || !Object.keys(changes).length} onClick={() => setChanges({})}>Clear Changes</button><button className="tx-primary" disabled={busy || !Object.keys(changes).length} onClick={() => void saveReconciliation()}>Save Reconciliation</button></div></>}
    </main>
    {fine && <Dialog title="Add Traffic Fine" onClose={() => { if (!busy && window.confirm('Discard unsaved traffic fine?')) setFine(null); }}><div className="tx-editor-body">{fineError && <div className="tx-error" role="alert">{fineError}</div>}<div className="tx-fields">
      <label>Traffic file<select value={fine.trafficFile} onChange={e => setFine({ ...fine, trafficFile: e.target.value })}><option value="">Select traffic file</option>{lookups.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}</select></label>
      {field('fineDate', 'Fine date and time', 'datetime-local')}{field('authority', 'Fine authority')}
      <label>Vehicle<Picker name="vehicles" label="Vehicle" value={fine.vehicleId} onChange={value => setFine({ ...fine, vehicleId: value })} /></label>
      {field('ticketNo', 'Ticket number')}{field('amount', 'Amount', 'number')}{field('blackPoints', 'Black points', 'number')}{field('acknowledgment', 'Acknowledgment', 'number')}
    </div><label>Fine description<textarea value={fine.description} onChange={e => setFine({ ...fine, description: e.target.value })} /></label></div><footer className="tx-footer"><button disabled={busy} onClick={() => setFine(null)}>Close</button><button className="tx-primary" disabled={busy} onClick={() => void saveFine()}>{busy ? 'Saving...' : 'Save'}</button></footer></Dialog>}
  </div></div>;
}

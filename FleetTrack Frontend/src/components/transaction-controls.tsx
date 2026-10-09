"use client";

import { useEffect, useId, useRef, useState } from 'react';
import { lookup, type Lookup, type Row } from '@/lib/transactions';

export function Picker({ name, value, onChange, disabled = false, label }: {
  name: string; value: string; onChange: (value: string) => void; disabled?: boolean; label: string;
}) {
  const [options, setOptions] = useState<Lookup[]>([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Lookup | null>(null);
  const id = useId();
  useEffect(() => {
    let active = true;
    const timeout = setTimeout(() => {
      lookup(name, search).then(rows => { if (active) { setOptions(rows); setError(''); } }).catch(() => { if (active) setError('Could not load choices'); });
    }, 180);
    return () => { active = false; clearTimeout(timeout); };
  }, [name, search]);
  useEffect(() => {
    let active = true;
    if (value) lookup(name, '', value).then(rows => { if (active) setSelected(rows[0] || null); }).catch(() => {});
    return () => { active = false; };
  }, [name, value]);
  const rows = selected && String(selected.id) === value && !options.some(row => String(row.id) === value) ? [selected, ...options] : options;
  return <div className="tx-picker">
    {!disabled && <input aria-label={`Search ${label}`} placeholder={`Search ${label.toLowerCase()}`} value={search} onChange={event => setSearch(event.target.value)} />}
    <select id={id} aria-label={label} value={value} disabled={disabled} onChange={event => onChange(event.target.value)}>
      <option value="">Select {label.toLowerCase()}</option>
      {value && !rows.some(row => String(row.id) === value) && <option value={value}>{value}</option>}
      {rows.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}
    </select>
    {error && <small role="alert">{error}</small>}
  </div>;
}

export function Dialog({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { const dialog = ref.current; dialog?.showModal(); return () => dialog?.close(); }, []);
  return <dialog ref={ref} className="tx-dialog" onCancel={event => { event.preventDefault(); onClose(); }} aria-label={title}>
    <header><h2>{title}</h2><button type="button" onClick={onClose} aria-label="Close" title="Close">×</button></header>
    {children}
  </dialog>;
}

export function printDocument(title: string, header: Row, lines: Row[], target = window.open('', '_blank')) {
  if (!target) throw new Error('Allow pop-ups to print');
  target.opener = null;
  const doc = target.document;
  doc.title = title;
  const style = doc.createElement('style');
  style.textContent = 'body{font:12px Arial;margin:24px;color:#17212c}h1{font-size:20px}dl{display:grid;grid-template-columns:160px 1fr;gap:8px}dt{font-weight:bold}dd{margin:0}table{border-collapse:collapse;width:100%;font-size:10px}td,th{border:1px solid #bbb;padding:6px;text-align:left}button{margin:12px 0}@media print{button{display:none}}';
  doc.head.append(style);
  const h1 = doc.createElement('h1'); h1.textContent = title; doc.body.append(h1);
  const dl = doc.createElement('dl');
  for (const [key, value] of Object.entries(header)) {
    if (value == null || key.startsWith('extra') || key.endsWith('Id')) continue;
    const dt = doc.createElement('dt'); dt.textContent = key.replace(/([A-Z])/g, ' $1');
    const dd = doc.createElement('dd'); dd.textContent = String(value); dl.append(dt, dd);
  }
  doc.body.append(dl);
  const keys = Object.keys(lines[0] || {}).filter(key => !key.startsWith('extra') && key !== 'id');
  const table = doc.createElement('table'), tr = doc.createElement('tr');
  keys.forEach(key => { const th = doc.createElement('th'); th.textContent = key; tr.append(th); }); table.append(tr);
  lines.forEach(row => { const tr = doc.createElement('tr'); keys.forEach(key => { const td = doc.createElement('td'); td.textContent = String(row[key] ?? ''); tr.append(td); }); table.append(tr); });
  doc.body.append(table);
  const button = doc.createElement('button'); button.textContent = 'Print'; button.onclick = () => target.print(); doc.body.append(button);
  target.focus(); target.print();
}

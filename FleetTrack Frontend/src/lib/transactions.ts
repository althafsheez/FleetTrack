import { request } from './api';

export type Value = string | number | boolean | null;
export type Row = Record<string, Value>;
export type Lookup = { id: string | number; name: string; rate?: string | number };
export type DocumentKind = 'purchase-orders' | 'purchase-invoices' | 'sales-quotations' | 'credit-notes' | 'debit-notes' | 'vehicle-finance';
export type TransactionDocument = { id: number; header: Row; lines: Row[]; taxes: Row[]; allocations?: Row[]; version: string };
export type Register = { items: Row[]; total: number; offset: number; limit: number; bookBalance?: number | string };
export const titles: Record<DocumentKind, string> = {
  'purchase-orders': 'Purchase Orders', 'purchase-invoices': 'Purchase Invoices', 'sales-quotations': 'Sales Quotations',
  'credit-notes': 'Credit Notes (Invoice)', 'debit-notes': 'Debit Notes', 'vehicle-finance': 'Vehicle Finance',
};
export function query(values: Record<string, string | number | boolean | null | undefined>) {
  const result = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => { if (value !== '' && value != null) result.set(key, String(value)); });
  return `?${result}`;
}
export function lookup(name: string, q = '', selected?: string) {
  return request<Lookup[]>(`/transaction-documents/lookups/${name}${query({ q, selected })}`);
}
export function today() {
  const date = new Date();
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
export function dateText(value: Value | undefined) {
  if (!value) return '-';
  return String(value).slice(0, 10).split('-').reverse().join('/');
}
export function money(value: Value | undefined) {
  return Number(value || 0).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
export function csv(rows: Row[], name: string) {
  if (!rows.length) return;
  const keys = Object.keys(rows[0]);
  const cell = (value: unknown) => {
    let result = String(value ?? '');
    if (/^[=+@\-\t\r]/.test(result)) result = `'${result}`;
    return `"${result.replaceAll('"', '""')}"`;
  };
  const content = [keys.map(cell).join(','), ...rows.map(row => keys.map(key => cell(row[key])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a'); link.href = url; link.download = `${name}.csv`; link.click(); URL.revokeObjectURL(url);
}

"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout, type AuthenticatedUser } from "@/lib/api";

type Customer = {
  id: string; name: string; arabicName: string; corporate: boolean; mobile: string;
  email: string; emirate: string; customerIdNo: string; expiry: string; creditLimit: string;
};

const demoCustomers: Customer[] = [
  { id: "CUST-DEMO-1041", name: "Demo Logistics LLC", arabicName: "[Demo] Logistics account", corporate: true, mobile: "+971 50 882 1904", email: "demo.logistics@example.test", emirate: "Dubai", customerIdNo: "DEMO-DXB-992014", expiry: "14 Dec 2026", creditLimit: "AED 100,000.00" },
  { id: "CUST-DEMO-1042", name: "Demo Distribution", arabicName: "[Demo] Corporate account", corporate: true, mobile: "+971 52 411 9002", email: "demo.distribution@example.test", emirate: "Dubai", customerIdNo: "DEMO-DXB-441029", expiry: "28 Jun 2027", creditLimit: "AED 250,000.00" },
  { id: "CUST-DEMO-1043", name: "Demo Individual A", arabicName: "[Demo] Individual account", corporate: false, mobile: "+971 50 119 4432", email: "demo.individual.a@example.test", emirate: "Abu Dhabi", customerIdNo: "DEMO-EID-001", expiry: "04 May 2027", creditLimit: "AED 15,000.00" },
  { id: "CUST-DEMO-1044", name: "Demo Travel Services", arabicName: "[Demo] Corporate account", corporate: true, mobile: "+971 55 304 1178", email: "demo.travel@example.test", emirate: "Sharjah", customerIdNo: "DEMO-SHJ-220817", expiry: "19 Feb 2028", creditLimit: "AED 75,000.00" },
  { id: "CUST-DEMO-1045", name: "Demo Individual B", arabicName: "[Demo] Individual account", corporate: false, mobile: "+971 56 720 4510", email: "demo.individual.b@example.test", emirate: "Dubai", customerIdNo: "DEMO-EID-002", expiry: "10 Aug 2027", creditLimit: "AED 10,000.00" },
  { id: "CUST-DEMO-1046", name: "Demo Construction Co.", arabicName: "[Demo] Corporate account", corporate: true, mobile: "+971 54 871 6609", email: "demo.construction@example.test", emirate: "Ajman", customerIdNo: "DEMO-AJM-094117", expiry: "23 Nov 2026", creditLimit: "AED 130,000.00" },
  { id: "CUST-DEMO-1047", name: "Demo Hospitality Group", arabicName: "[Demo] Corporate account", corporate: true, mobile: "+971 58 244 1730", email: "demo.hospitality@example.test", emirate: "Ras Al Khaimah", customerIdNo: "DEMO-RAK-774011", expiry: "08 Mar 2028", creditLimit: "AED 90,000.00" },
  { id: "CUST-DEMO-1048", name: "Demo Individual C", arabicName: "[Demo] Individual account", corporate: false, mobile: "+971 50 675 3921", email: "demo.individual.c@example.test", emirate: "Fujairah", customerIdNo: "DEMO-EID-003", expiry: "16 Sep 2027", creditLimit: "AED 12,000.00" },
  { id: "CUST-DEMO-1049", name: "Demo Events Management", arabicName: "[Demo] Corporate account", corporate: true, mobile: "+971 55 902 8634", email: "demo.events@example.test", emirate: "Dubai", customerIdNo: "DEMO-DXB-551068", expiry: "25 Jan 2028", creditLimit: "AED 65,000.00" },
  { id: "CUST-DEMO-1050", name: "Demo Individual D", arabicName: "[Demo] Individual account", corporate: false, mobile: "+971 52 376 1940", email: "demo.individual.d@example.test", emirate: "Umm Al Quwain", customerIdNo: "DEMO-EID-004", expiry: "30 Jul 2027", creditLimit: "AED 8,000.00" },
];

const glyph: Record<string, string> = { dashboard: "⊞", group: "♙", directions_car: "◆", payments: "¤", description: "▤", expand_more: "⌄", storefront: "⌂", notifications: "●", logout: "⇥", add: "+", visibility: "◉", edit: "✎", delete: "×", close: "×", save: "✓", person_add: "⊕", settings: "⚙", sensors: "◌", menu_open: "≪", filter: "⌕" };
function Icon({ name }: { name: string }) { return <span aria-hidden className="cu-icon">{glyph[name] ?? "•"}</span>; }

export default function CustomersPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [nameQuery, setNameQuery] = useState("");
  const [mobileQuery, setMobileQuery] = useState("");
  const [drawer, setDrawer] = useState<"create" | "view" | "edit" | null>(null);
  const [selected, setSelected] = useState<Customer>(demoCustomers[0]);

  useEffect(() => { getCurrentUser().then(setUser).catch(() => router.replace("/login")).finally(() => setChecking(false)); }, [router]);
  const visibleCustomers = useMemo(() => demoCustomers.filter((customer) => customer.name.toLowerCase().includes(nameQuery.toLowerCase()) && customer.mobile.includes(mobileQuery)), [nameQuery, mobileQuery]);
  async function signOut() { try { await logout(); } finally { router.replace("/login"); } }
  function open(customer: Customer, mode: "view" | "edit") { setSelected(customer); setDrawer(mode); }
  if (checking) return <main className="ft-loading">Checking your FleetTrack session…</main>;
  if (!user) return null;

  return <div className="cu-app">
    <aside className="cu-sidebar">
      <div><div className="cu-brand"><span>▰</span><div><b>FleetTrack</b><small>Enterprise Logistics v4.2</small></div></div>
        <nav>
          <Link href="/dashboard"><Icon name="dashboard" />Dashboard</Link>
          <Link className="cu-active" href="/customers"><Icon name="group" />Customers <em>[Demo]</em></Link>
          <a href="#vehicles"><Icon name="directions_car" />Vehicles</a><a href="#tariffs"><Icon name="payments" />Tariffs</a>
          <a href="#contracts"><Icon name="description" />Contracts <span className="cu-chevron">⌄</span></a>
          <div className="cu-subnav"><a href="#add-contract">• Add Contract</a><a href="#view-contracts">• View Contracts</a></div>
        </nav></div>
      <div className="cu-side-footer"><a href="#status"><Icon name="sensors" />System Status</a><a href="#settings"><Icon name="settings" />Settings</a><button type="button"><Icon name="menu_open" />Collapse Menu</button></div>
    </aside>
    <div className="cu-frame">
      <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Operations</span><span>/</span><strong>Customers</strong><i /></div>
        <div className="cu-user"><button type="button"><Icon name="storefront" /></button><button className="cu-notice" type="button"><Icon name="notifications" /></button><i /><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={signOut} type="button"><Icon name="logout" />Logout</button></div>
      </header>
      <main className="cu-main">
        <div className="cu-page-heading"><div><h1>Customers <small>(Demo UI)</small></h1><p>Manage customer contact, identification, credit, and account information.</p></div><button className="cu-primary" onClick={() => setDrawer("create")} type="button"><Icon name="add" />Add Customer</button></div>
        <section className="cu-filter-panel"><div><label>Customer Name</label><span><input onChange={(event) => setNameQuery(event.target.value)} placeholder="Search by name…" value={nameQuery} />{nameQuery && <button aria-label="Clear name search" onClick={() => setNameQuery("")} type="button"><Icon name="close" /></button>}</span></div><div><label>Mobile Number</label><input onChange={(event) => setMobileQuery(event.target.value)} placeholder="+971 50…" value={mobileQuery} /></div><button className="cu-filter-button" type="button"><Icon name="filter" />Search</button><button className="cu-clear" onClick={() => { setNameQuery(""); setMobileQuery(""); }} type="button">Clear</button></section>
        <div className="cu-list-meta"><span>Showing <b>{visibleCustomers.length}</b> demo customers</span><span>Demo UI — not connected to customer records yet</span></div>
        <section className="cu-table-card"><div className="cu-table-wrap"><table><thead><tr><th>Customer ID</th><th>Customer Name</th><th>Type</th><th>Mobile</th><th>Email</th><th>Emirate</th><th>Customer ID No</th><th>ID Expiry</th><th>Credit Limit</th><th>Actions</th></tr></thead><tbody>{visibleCustomers.map((customer) => <tr key={customer.id}><td><code>{customer.id}</code></td><td><b>{customer.name}</b><small>{customer.arabicName}</small></td><td><span className={customer.corporate ? "cu-type corporate" : "cu-type individual"}><i />{customer.corporate ? "Corporate" : "Individual"} <em>(Demo)</em></span></td><td><code>{customer.mobile}</code></td><td className="cu-email">{customer.email}</td><td><span className="cu-emirate">{customer.emirate}</span></td><td><code>{customer.customerIdNo}</code></td><td><code>{customer.expiry}</code></td><td className="cu-credit">{customer.creditLimit}</td><td><div className="cu-actions"><button aria-label="View customer" onClick={() => open(customer, "view")} type="button"><Icon name="visibility" /></button><button aria-label="Edit customer" onClick={() => open(customer, "edit")} type="button"><Icon name="edit" /></button><button aria-label="Delete unavailable in demo UI" disabled type="button"><Icon name="delete" /></button></div></td></tr>)}</tbody></table></div></section>
      </main>
    </div>
    {drawer && <CustomerDrawer customer={selected} mode={drawer} onClose={() => setDrawer(null)} onEdit={() => setDrawer("edit")} />}
  </div>;
}

function CustomerDrawer({ customer, mode, onClose, onEdit }: { customer: Customer; mode: "create" | "view" | "edit"; onClose: () => void; onEdit: () => void }) {
  const editable = mode !== "view";
  const title = mode === "create" ? "Add Customer" : mode === "edit" ? "Edit Customer" : "Customer Details";
  return <div className="cu-drawer-backdrop" role="presentation"><aside aria-label={title} className="cu-drawer"><header><div><small>{mode === "create" ? "NEW CUSTOMER" : "CUSTOMER RECORD"}</small><h2>{title} <em>(Demo UI)</em></h2></div><button aria-label="Close drawer" onClick={onClose} type="button"><Icon name="close" /></button></header>
    <div className="cu-drawer-content">{editable ? <CustomerForm customer={mode === "create" ? undefined : customer} /> : <CustomerView customer={customer} />}</div>
    <footer>{mode === "view" ? <><button onClick={onClose} type="button">Close</button><button className="cu-primary" onClick={onEdit} type="button"><Icon name="edit" />Edit Customer</button></> : <><button onClick={onClose} type="button">Cancel</button><button className="cu-primary" type="button"><Icon name={mode === "create" ? "person_add" : "save"} />{mode === "create" ? "Save Customer" : "Update Customer"}</button></>}<p>Demo UI only — no customer record will be created or changed.</p></footer>
  </aside></div>;
}

function CustomerView({ customer }: { customer: Customer }) {
  return <div className="cu-details"><DetailSection title="1. Basic"><Detail label="Customer Name" value={customer.name} /><Detail label="Arabic / secondary name" value={customer.arabicName} /><Detail label="Customer Type" value={customer.corporate ? "Corporate (Demo)" : "Individual (Demo)"} /><Detail label="Emirate" value={customer.emirate} /></DetailSection><DetailSection title="2. Contact"><Detail label="Mobile" value={customer.mobile} /><Detail label="Email" value={customer.email} /><Detail label="Phone" value="[Demo] +971 4 000 0000" /><Detail label="Address" value="[Demo] Dubai, United Arab Emirates" /></DetailSection><DetailSection title="3. Identification"><Detail label="Customer ID number" value={customer.customerIdNo} /><Detail label="Customer ID expiry" value={customer.expiry} /><Detail label="Tax number / TRN" value="[Demo] 100000000000000" /></DetailSection><DetailSection title="4. Account"><Detail label="Credit limit" value={customer.creditLimit} /><Detail label="Credit period" value="[Demo] 30 days" /><Detail label="Bill-by-Bill" value="[Demo] Enabled" /></DetailSection></div>;
}
function DetailSection({ title, children }: { title: string; children: React.ReactNode }) { return <section><h3>{title}</h3><div>{children}</div></section>; }
function Detail({ label, value }: { label: string; value: string }) { return <p><small>{label}</small><b>{value}</b></p>; }

function CustomerForm({ customer }: { customer?: Customer }) {
  const base = customer ?? { name: "", corporate: false, mobile: "", email: "", emirate: "Dubai", customerIdNo: "", expiry: "", creditLimit: "" };
  return <form className="cu-form" onSubmit={(event) => event.preventDefault()}>
    <FormSection title="1. Basic"><Field label="Customer Name *" defaultValue={base.name} required /><Field label="Arabic Name" defaultValue={customer?.arabicName} /><Field label="Mailing Name" defaultValue={customer?.name} /><Choice label="Customer Type" /></FormSection>
    <FormSection title="2. Contact"><Field label="Mobile Number *" defaultValue={base.mobile} required type="tel" /><Field label="Phone Number" /><Field label="Email" defaultValue={base.email} type="email" /><Field label="Address" area /></FormSection>
    <FormSection title="3. Identification"><Field label="Customer ID Number" defaultValue={base.customerIdNo} /><Field label="Customer ID Expiry" defaultValue={base.expiry ? "2027-12-14" : ""} type="date" /><Field label="Tax Number (TRN)" /><Field label="Nationality (max 3 chars)" maxLength={3} /></FormSection>
    <FormSection title="4. Account"><Field label="Opening Balance" type="number" /><SelectField label="Debit / Credit" options={["Dr (Debit)", "Cr (Credit)"]} /><Field label="Credit Period (days)" type="number" /><Field label="Credit Limit" defaultValue={base.creditLimit.replace("AED ", "").replace(",", "")} type="number" /><Check label="Bill-by-Bill Settlement" /><Field label="Bank Account Number" /></FormSection>
    <FormSection title="5. Organization"><Field label="Branch Name" /><Field label="Branch Code" /><Field label="Route ID" type="number" /><Field label="Area ID" type="number" /></FormSection>
    <FormSection title="6. Notes"><Field label="Narration" area /></FormSection>
  </form>;
}
function FormSection({ title, children }: { title: string; children: React.ReactNode }) { return <section><h3>{title}</h3><div className="cu-form-grid">{children}</div></section>; }
function Field({ label, defaultValue, required, type = "text", area = false, maxLength }: { label: string; defaultValue?: string; required?: boolean; type?: string; area?: boolean; maxLength?: number }) { return <label className={area ? "cu-form-full" : ""}>{label}{area ? <textarea defaultValue={defaultValue} /> : <input defaultValue={defaultValue} maxLength={maxLength} required={required} type={type} />}</label>; }
function SelectField({ label, options }: { label: string; options: string[] }) { return <label>{label}<select>{options.map((option) => <option key={option}>{option}</option>)}</select></label>; }
function Choice({ label }: { label: string }) { return <fieldset><legend>{label}</legend><label><input defaultChecked name="corporate" type="radio" />Corporate</label><label><input name="corporate" type="radio" />Individual</label></fieldset>; }
function Check({ label }: { label: string }) { return <label className="cu-check"><input type="checkbox" />{label}</label>; }

"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createCustomer, getCurrentUser, getCustomersPage, logout, searchCustomersPage, updateCustomer, type AuthenticatedUser, type CustomerPayload, type CustomerRecord } from "@/lib/api";
import { FleetSidebar } from "@/components/fleet-sidebar";

type Customer = {
  id: string; apiId?: number; raw?: CustomerRecord; name: string; arabicName: string; corporate: boolean; mobile: string;
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

function customerFromApi(record: CustomerRecord): Customer {
  const expiry = record.CustomerIdExpiry ? new Date(record.CustomerIdExpiry).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "—";
  const credit = record.creditLimit === null || record.creditLimit === undefined ? "—" : `AED ${Number(record.creditLimit).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  return {
    id: record.ledgerId ? `LEDGER-${record.ledgerId}` : "LEDGER—",
    apiId: record.ledgerId,
    raw: record,
    name: record.ledgerName || "Unnamed customer",
    arabicName: record.ledgerNameInArabic || "—",
    corporate: Boolean(record.isCorporate),
    mobile: record.mobile || "—",
    email: record.email || "—",
    emirate: record.emirateId ? `Emirate #${record.emirateId}` : "—",
    customerIdNo: record.CustomerIdNo || "—",
    expiry,
    creditLimit: credit,
  };
}

const glyph: Record<string, string> = { dashboard: "⊞", group: "♙", directions_car: "◆", payments: "¤", description: "▤", expand_more: "⌄", storefront: "⌂", notifications: "●", logout: "⇥", add: "+", visibility: "◉", edit: "✎", delete: "×", close: "×", save: "✓", person_add: "⊕", settings: "⚙", sensors: "◌", menu_open: "≪", filter: "⌕" };
function Icon({ name }: { name: string }) { return <span aria-hidden className="cu-icon">{glyph[name] ?? "•"}</span>; }

export default function CustomersPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [nameQuery, setNameQuery] = useState("");
  const [mobileQuery, setMobileQuery] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [totalCustomers, setTotalCustomers] = useState(0);
  const [offset, setOffset] = useState(0);
  const pageSize = 10;
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [customerError, setCustomerError] = useState<string | null>(null);
  const [drawer, setDrawer] = useState<"create" | "view" | "edit" | null>(null);
  const [selected, setSelected] = useState<Customer>(demoCustomers[0]);

  useEffect(() => {
    async function load() {
      try {
        const activeUser = await getCurrentUser();
        setUser(activeUser);
        const page = await getCustomersPage(0, pageSize);
        setCustomers(page.items.map(customerFromApi));
        setTotalCustomers(page.total);
      } catch (error) {
        if (error instanceof Error && error.message.includes("session")) router.replace("/login");
        else setCustomerError(error instanceof Error ? error.message : "Customer records could not be loaded.");
      } finally {
        setChecking(false);
        setLoadingCustomers(false);
      }
    }
    void load();
  }, [router]);
  const visibleCustomers = useMemo(() => customers, [customers]);
  const totalPages = Math.max(1, Math.ceil(totalCustomers / pageSize));
  const currentPage = Math.floor(offset / pageSize) + 1;
  const firstVisiblePage = Math.max(1, Math.min(currentPage - 2, totalPages - 4));
  const pageNumbers = Array.from({ length: Math.min(5, totalPages) }, (_, index) => firstVisiblePage + index);
  async function signOut() { try { await logout(); } finally { router.replace("/login"); } }
  async function loadPage(nextOffset: number, search = Boolean(nameQuery.trim() || mobileQuery.trim())) {
    setLoadingCustomers(true); setCustomerError(null);
    try {
      const page = search ? await searchCustomersPage(nextOffset, pageSize, nameQuery, mobileQuery) : await getCustomersPage(nextOffset, pageSize);
      setCustomers(page.items.map(customerFromApi)); setTotalCustomers(page.total); setOffset(page.offset);
    } catch (error) { setCustomerError(error instanceof Error ? error.message : "Customer records could not be completed."); }
    finally { setLoadingCustomers(false); }
  }
  async function runSearch() { await loadPage(0, true); }
  async function clearSearch() {
    setNameQuery(""); setMobileQuery(""); setLoadingCustomers(true); setCustomerError(null);
    try {
      const page = await getCustomersPage(0, pageSize);
      setCustomers(page.items.map(customerFromApi)); setTotalCustomers(page.total); setOffset(page.offset);
    } catch (error) { setCustomerError(error instanceof Error ? error.message : "Customer records could not be loaded."); }
    finally { setLoadingCustomers(false); }
  }
  function open(customer: Customer, mode: "view" | "edit") { setSelected(customer); setDrawer(mode); }
  if (checking) return <main className="ft-loading">Checking your FleetTrack session…</main>;
  if (!user) return null;

  return <div className="cu-app">
    <FleetSidebar />
    <div className="cu-frame">
      <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Operations</span><span>/</span><strong>Customers</strong><i /></div>
        <div className="cu-user"><button type="button"><Icon name="storefront" /></button><button className="cu-notice" type="button"><Icon name="notifications" /></button><i /><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={signOut} type="button"><Icon name="logout" />Logout</button></div>
      </header>
      <main className="cu-main">
        <div className="cu-page-heading"><div><h1>Customers</h1><p>Manage customer contact, identification, credit, and account information.</p></div><button className="cu-primary" onClick={() => setDrawer("create")} type="button"><Icon name="add" />Add Customer</button></div>
        <section className="cu-filter-panel"><div><label>Customer Name</label><span><input onChange={(event) => setNameQuery(event.target.value)} placeholder="Search by name…" value={nameQuery} />{nameQuery && <button aria-label="Clear name search" onClick={() => setNameQuery("")} type="button"><Icon name="close" /></button>}</span></div><div><label>Mobile Number</label><input onChange={(event) => setMobileQuery(event.target.value)} placeholder="+971 50…" value={mobileQuery} /></div><button className="cu-filter-button" onClick={runSearch} type="button"><Icon name="filter" />Search</button><button className="cu-clear" onClick={clearSearch} type="button">Clear</button></section>
        <div className="cu-list-meta"><span>{loadingCustomers ? "Loading customer records…" : <>Showing <b>{totalCustomers ? offset + 1 : 0}–{Math.min(offset + pageSize, totalCustomers)}</b> of <b>{totalCustomers}</b> customer records</>}</span><span>Connected to the customer API</span></div>
        {customerError && <p className="cu-api-error">{customerError}</p>}
        <section className="cu-table-card"><div className="cu-table-wrap"><table><thead><tr><th className="cu-sticky-action">Actions</th><th>Customer ID</th><th>Customer Name</th><th>Type</th><th>Mobile</th><th>Email</th><th>Emirate</th><th>Credit Limit</th></tr></thead><tbody>{visibleCustomers.map((customer) => <tr key={customer.id}><td className="cu-sticky-action"><div className="cu-actions"><button aria-label="View customer" onClick={() => open(customer, "view")} type="button"><Icon name="visibility" /></button><button aria-label="Edit customer" onClick={() => open(customer, "edit")} type="button"><Icon name="edit" /></button><button aria-label="Delete unavailable until approved" disabled type="button"><Icon name="delete" /></button></div></td><td><code>{customer.id}</code></td><td><b>{customer.name}</b><small>{customer.arabicName}</small></td><td><span className={customer.corporate ? "cu-type corporate" : "cu-type individual"}><i />{customer.corporate ? "Corporate" : "Individual"}</span></td><td><code>{customer.mobile}</code></td><td className="cu-email">{customer.email}</td><td><span className="cu-emirate">{customer.emirate}</span></td><td className="cu-credit">{customer.creditLimit}</td></tr>)}</tbody></table></div><footer className="cu-pagination"><span>Page {currentPage} of {totalPages}</span><div><button disabled={offset === 0 || loadingCustomers} onClick={() => loadPage(Math.max(0, offset - pageSize))} type="button">Previous</button>{pageNumbers.map((page) => <button aria-current={page === currentPage ? "page" : undefined} className={page === currentPage ? "cu-page-active" : ""} disabled={loadingCustomers || page === currentPage} key={page} onClick={() => loadPage((page - 1) * pageSize)} type="button">{page}</button>)}<button disabled={offset + pageSize >= totalCustomers || loadingCustomers} onClick={() => loadPage(offset + pageSize)} type="button">Next</button></div></footer></section>
      </main>
    </div>
    {drawer && <CustomerDrawer customer={selected} mode={drawer} onClose={() => setDrawer(null)} onEdit={() => setDrawer("edit")} onSaved={() => { setDrawer(null); void loadPage(offset); }} />}
  </div>;
}

function CustomerDrawer({ customer, mode, onClose, onEdit, onSaved }: { customer: Customer; mode: "create" | "view" | "edit"; onClose: () => void; onEdit: () => void; onSaved: () => void }) {
  const editable = mode !== "view";
  const title = mode === "create" ? "Add Customer" : mode === "edit" ? "Edit Customer" : "Customer Details";
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function submit(form: HTMLFormElement) {
    const values = new FormData(form);
    const optionalText = (name: string) => String(values.get(name) || "").trim() || null;
    const optionalNumber = (name: string) => {
      const value = optionalText(name);
      return value === null ? null : Number(value);
    };
    const ledgerName = String(values.get("ledgerName") || "").trim();
    const mobile = String(values.get("mobile") || "").trim();
    const emirateId = Number(values.get("emirateId"));
    const email = optionalText("email");
    if (!ledgerName) { setError("Customer Name is required."); return; }
    if (mobile.length < 10) { setError("Mobile Number must contain at least 10 characters."); return; }
    if (!Number.isInteger(emirateId) || emirateId < 1 || emirateId > 7) { setError("Please choose a valid Emirate."); return; }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setError("Enter a valid email address, for example name@company.ae."); return; }
    const payload: CustomerPayload = {
      ledgerName,
      ledgerNameInArabic: optionalText("ledgerNameInArabic"),
      openingBalance: optionalNumber("openingBalance"),
      crOrDr: optionalText("crOrDr"),
      emirateId,
      mailingName: optionalText("mailingName"),
      bankAccountNumber: optionalText("bankAccountNumber"),
      branchName: optionalText("branchName"),
      branchCode: optionalText("branchCode"),
      phone: optionalText("phone"),
      mobile,
      email,
      address: optionalText("address"),
      creditPeriod: optionalNumber("creditPeriod"),
      creditLimit: optionalNumber("creditLimit"),
      billByBill: values.get("billByBill") === "on",
      tin: optionalText("tin"),
      narration: optionalText("narration"),
      Nationality: optionalText("Nationality"),
      CustomerIdNo: optionalText("CustomerIdNo"),
      CustomerIdExpiry: optionalText("CustomerIdExpiry"),
      routeId: optionalNumber("routeId"),
      areaId: optionalNumber("areaId"),
      isCorporate: values.get("isCorporate") === "true",
    };
    setSaving(true); setError(null);
    try {
      if (mode === "create") await createCustomer(payload);
      else if (customer.apiId) await updateCustomer(customer.apiId, payload);
      else throw new Error("This customer record has no editable ledger ID.");
      onSaved();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The customer could not be saved."); }
    finally { setSaving(false); }
  }
  return <div className="cu-drawer-backdrop" role="presentation"><aside aria-label={title} className="cu-drawer"><header><div><small>{mode === "create" ? "NEW CUSTOMER" : "CUSTOMER RECORD"}</small><h2>{title}</h2></div><button aria-label="Close drawer" onClick={onClose} type="button"><Icon name="close" /></button></header>
    <div className="cu-drawer-content">{error && <p className="cu-api-error">{error}</p>}{editable ? <CustomerForm customer={mode === "create" ? undefined : customer} onSubmit={submit} /> : <CustomerView customer={customer} />}</div>
    <footer>{mode === "view" ? <><button onClick={onClose} type="button">Close</button><button className="cu-primary" onClick={onEdit} type="button"><Icon name="edit" />Edit Customer</button></> : <><button onClick={onClose} type="button">Cancel</button><button className="cu-primary" disabled={saving} form="customer-form" type="submit"><Icon name={mode === "create" ? "person_add" : "save"} />{saving ? "Saving…" : mode === "create" ? "Save Customer" : "Update Customer"}</button></>}<p>{editable ? "Changes are sent to the FleetTrack customer API only when you save." : "Customer record loaded from the FleetTrack customer API."}</p></footer>
  </aside></div>;
}

function CustomerView({ customer }: { customer: Customer }) {
  const record = customer.raw;
  const value = (entry: unknown) => entry === null || entry === undefined || entry === "" ? "—" : String(entry);
  return <div className="cu-details"><DetailSection title="1. Basic"><Detail label="Customer Name" value={customer.name} /><Detail label="Arabic / secondary name" value={customer.arabicName} /><Detail label="Customer Type" value={customer.corporate ? "Corporate" : "Individual"} /><Detail label="Emirate" value={customer.emirate} /><Detail label="Mailing name" value={value(record?.mailingName)} /></DetailSection><DetailSection title="2. Contact"><Detail label="Mobile" value={customer.mobile} /><Detail label="Email" value={customer.email} /><Detail label="Phone" value={value(record?.phone)} /><Detail label="Address" value={value(record?.address)} /></DetailSection><DetailSection title="3. Identification"><Detail label="Customer ID number" value={customer.customerIdNo} /><Detail label="Customer ID expiry" value={customer.expiry} /><Detail label="Tax number / TRN" value={value(record?.tin)} /><Detail label="Nationality" value={value(record?.Nationality)} /></DetailSection><DetailSection title="4. Account"><Detail label="Opening balance" value={value(record?.openingBalance)} /><Detail label="Debit / credit" value={value(record?.crOrDr)} /><Detail label="Credit limit" value={customer.creditLimit} /><Detail label="Credit period" value={record?.creditPeriod === null || record?.creditPeriod === undefined ? "—" : `${record.creditPeriod} days`} /><Detail label="Bill-by-Bill" value={record?.billByBill ? "Enabled" : "Not enabled"} /><Detail label="Bank account" value={value(record?.bankAccountNumber)} /></DetailSection><DetailSection title="5. Organization & Notes"><Detail label="Branch" value={value(record?.branchName)} /><Detail label="Branch code" value={value(record?.branchCode)} /><Detail label="Route ID" value={value(record?.routeId)} /><Detail label="Area ID" value={value(record?.areaId)} /><Detail label="Narration" value={value(record?.narration)} /></DetailSection></div>;
}
function DetailSection({ title, children }: { title: string; children: React.ReactNode }) { return <section><h3>{title}</h3><div>{children}</div></section>; }
function Detail({ label, value }: { label: string; value: string }) { return <p><small>{label}</small><b>{value}</b></p>; }

function CustomerForm({ customer, onSubmit }: { customer?: Customer; onSubmit: (form: HTMLFormElement) => Promise<void> }) {
  const record = customer?.raw;
  const date = record?.CustomerIdExpiry?.slice(0, 10) || "";
  return <form className="cu-form" id="customer-form" onSubmit={(event) => { event.preventDefault(); void onSubmit(event.currentTarget); }}>
    <FormSection title="1. Basic"><Field label="Customer Name *" name="ledgerName" defaultValue={record?.ledgerName} required /><Field label="Arabic Name" name="ledgerNameInArabic" defaultValue={record?.ledgerNameInArabic || ""} /><Field label="Mailing Name" name="mailingName" defaultValue={record?.mailingName || ""} /><Choice defaultCorporate={record?.isCorporate} label="Customer Type" /></FormSection>
    <FormSection title="2. Contact"><Field label="Mobile Number *" name="mobile" defaultValue={record?.mobile || ""} required type="tel" /><Field label="Phone Number" name="phone" defaultValue={record?.phone || ""} /><Field label="Email" name="email" defaultValue={record?.email || ""} type="email" /><Field label="Address" name="address" defaultValue={record?.address || ""} area /></FormSection>
    <FormSection title="3. Identification"><Field label="Customer ID Number" name="CustomerIdNo" defaultValue={record?.CustomerIdNo || ""} /><Field label="Customer ID Expiry" name="CustomerIdExpiry" defaultValue={date} type="date" /><Field label="Tax Number (TRN)" name="tin" defaultValue={record?.tin || ""} /><Field label="Nationality (max 3 chars)" name="Nationality" defaultValue={record?.Nationality || ""} maxLength={3} /></FormSection>
    <FormSection title="4. Account"><Field label="Opening Balance" name="openingBalance" defaultValue={record?.openingBalance?.toString() || ""} type="number" /><SelectField label="Debit / Credit" name="crOrDr" value={record?.crOrDr || "Dr"} options={["Dr", "Cr"]} /><Field label="Credit Period (days)" name="creditPeriod" defaultValue={record?.creditPeriod?.toString() || ""} type="number" /><Field label="Credit Limit" name="creditLimit" defaultValue={record?.creditLimit?.toString() || ""} type="number" /><Check defaultChecked={record?.billByBill || false} label="Bill-by-Bill Settlement" /><Field label="Bank Account Number" name="bankAccountNumber" defaultValue={record?.bankAccountNumber || ""} /></FormSection>
    <FormSection title="5. Organization"><SelectField label="Emirate *" name="emirateId" value={String(record?.emirateId || 1)} options={["1", "2", "3", "4", "5", "6", "7"]} /><Field label="Branch Name" name="branchName" defaultValue={record?.branchName || ""} /><Field label="Branch Code" name="branchCode" defaultValue={record?.branchCode || ""} /><Field label="Route ID" name="routeId" defaultValue={record?.routeId?.toString() || ""} type="number" /><Field label="Area ID" name="areaId" defaultValue={record?.areaId?.toString() || ""} type="number" /></FormSection>
    <FormSection title="6. Notes"><Field label="Narration" name="narration" defaultValue={record?.narration || ""} area /></FormSection>
  </form>;
}
function FormSection({ title, children }: { title: string; children: React.ReactNode }) { return <section><h3>{title}</h3><div className="cu-form-grid">{children}</div></section>; }
function Field({ label, name, defaultValue, required, type = "text", area = false, maxLength }: { label: string; name: string; defaultValue?: string; required?: boolean; type?: string; area?: boolean; maxLength?: number }) { return <label className={area ? "cu-form-full" : ""}>{label}{area ? <textarea defaultValue={defaultValue} name={name} /> : <input defaultValue={defaultValue} maxLength={maxLength} name={name} required={required} type={type} />}</label>; }
function SelectField({ label, name, options, value }: { label: string; name: string; options: string[]; value: string }) { return <label>{label}<select defaultValue={value} name={name}>{options.map((option) => <option key={option} value={option}>{name === "emirateId" ? `${option} — UAE Emirate` : option}</option>)}</select></label>; }
function Choice({ label, defaultCorporate }: { label: string; defaultCorporate?: boolean | null }) { return <fieldset><legend>{label}</legend><label><input defaultChecked={defaultCorporate !== false} name="isCorporate" type="radio" value="true" />Corporate</label><label><input defaultChecked={defaultCorporate === false} name="isCorporate" type="radio" value="false" />Individual</label></fieldset>; }
function Check({ label, defaultChecked }: { label: string; defaultChecked: boolean }) { return <label className="cu-check"><input defaultChecked={defaultChecked} name="billByBill" type="checkbox" />{label}</label>; }

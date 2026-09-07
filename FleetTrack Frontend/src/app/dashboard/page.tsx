"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout, type AuthenticatedUser } from "@/lib/api";

type Contract = {
  agreement: string;
  customer: string;
  detail: string;
  plate: string;
  vehicle: string;
  out: string;
  due: string;
  rate: string;
  status: "Overdue" | "Active" | "Check-in" | "Reserved";
};

const contracts: Contract[] = [
  { agreement: "AGR-DEMO-9104", customer: "Demo Customer A", detail: "[Demo] Corporate customer", plate: "DXB-DEMO-01", vehicle: "Toyota Hilux 2.7L", out: "12 Oct 2024", due: "24 Oct 2024", rate: "AED 180.00", status: "Overdue" },
  { agreement: "AGR-DEMO-9108", customer: "Demo Customer B", detail: "[Demo] Individual customer", plate: "AUH-DEMO-02", vehicle: "Nissan Patrol V8", out: "18 Oct 2024", due: "28 Oct 2024", rate: "AED 450.00", status: "Active" },
  { agreement: "AGR-DEMO-9092", customer: "Demo Customer C", detail: "[Demo] Contract preview", plate: "DXB-DEMO-03", vehicle: "Hyundai Sonata 2.5", out: "15 Oct 2024", due: "Today, 11:30", rate: "AED 135.00", status: "Check-in" },
  { agreement: "AGR-DEMO-9115", customer: "Demo Customer D", detail: "[Demo] Reservation preview", plate: "SHJ-DEMO-04", vehicle: "MG ZS 1.5L Comfort", out: "Today, 16:00", due: "02 Nov 2024", rate: "AED 110.00", status: "Reserved" },
  { agreement: "AGR-DEMO-9099", customer: "Demo Customer E", detail: "[Demo] Corporate customer", plate: "DXB-DEMO-05", vehicle: "Toyota Hiace 14-Seat", out: "14 Oct 2024", due: "14 Nov 2024", rate: "AED 260.00", status: "Active" },
  { agreement: "AGR-DEMO-9121", customer: "Demo Customer F", detail: "[Demo] Individual customer", plate: "DXB-DEMO-06", vehicle: "Kia Sportage 2.0", out: "16 Oct 2024", due: "26 Oct 2024", rate: "AED 160.00", status: "Active" },
  { agreement: "AGR-DEMO-9124", customer: "Demo Customer G", detail: "[Demo] Contract preview", plate: "AUH-DEMO-07", vehicle: "Mitsubishi Pajero", out: "17 Oct 2024", due: "27 Oct 2024", rate: "AED 210.00", status: "Reserved" },
  { agreement: "AGR-DEMO-9127", customer: "Demo Customer H", detail: "[Demo] Corporate customer", plate: "SHJ-DEMO-08", vehicle: "Ford Transit Van", out: "18 Oct 2024", due: "30 Oct 2024", rate: "AED 280.00", status: "Active" },
  { agreement: "AGR-DEMO-9130", customer: "Demo Customer I", detail: "[Demo] Individual customer", plate: "DXB-DEMO-09", vehicle: "Toyota Corolla 1.8", out: "19 Oct 2024", due: "29 Oct 2024", rate: "AED 120.00", status: "Check-in" },
  { agreement: "AGR-DEMO-9134", customer: "Demo Customer J", detail: "[Demo] Contract preview", plate: "AUH-DEMO-10", vehicle: "Chevrolet Tahoe", out: "20 Oct 2024", due: "01 Nov 2024", rate: "AED 390.00", status: "Active" },
];

const iconGlyph: Record<string, string> = {
  local_shipping: "▰", dashboard: "⊞", group: "♙", directions_car: "◆",
  payments: "¤", description: "▤", expand_less: "⌃", sensors: "◌",
  settings: "⚙", menu_open: "≪", storefront: "⌂", arrow_drop_down: "⌄",
  search: "⌕", notifications: "●", domain: "▦", logout: "⇥",
  file_download: "⇩", person_add: "⊕", note_add: "▧", speed: "◴",
  assignment: "▤", account_balance_wallet: "▣", sync_alt: "↔",
  refresh: "↻", more_vert: "⋮", notification_important: "!", event_repeat: "↻",
  fmd_bad: "!", build: "⌕",
};

function Icon({ children, className = "" }: { children: string; className?: string }) {
  return <span aria-hidden className={`material-symbols-outlined ${className}`}>{iconGlyph[children] ?? "•"}</span>;
}

function Status({ status }: { status: Contract["status"] }) {
  const tone = status === "Overdue" ? "ft-status-danger" : status === "Check-in" ? "ft-status-warning" : status === "Reserved" ? "ft-status-reserved" : "ft-status-active";
  return <span className={`ft-status ${tone}`}><span />{status} <em>(Demo)</em></span>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [signingOut, setSigningOut] = useState(false);

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => router.replace("/login")).finally(() => setCheckingSession(false));
  }, [router]);

  async function signOut() {
    setSigningOut(true);
    try { await logout(); } finally { router.replace("/login"); }
  }

  if (checkingSession) return <main className="ft-loading">Checking your FleetTrack session…</main>;
  if (!user) return null;

  return (
    <div className="ft-app">
      <aside className="ft-sidenav">
        <div className="ft-nav-top">
          <div className="ft-brand">
            <div className="ft-brand-mark"><Icon>local_shipping</Icon></div>
            <div><div className="ft-brand-name">FleetTrack</div><div className="ft-brand-version">Enterprise Logistics v4.2</div></div>
          </div>
          <nav className="ft-nav">
            <Link className="ft-nav-link ft-nav-active" href="/dashboard"><Icon>dashboard</Icon>Dashboard</Link>
            <Link className="ft-nav-link" href="/customers"><Icon>group</Icon>Customers</Link>
            <a className="ft-nav-link" href="#vehicles"><Icon>directions_car</Icon>Vehicles</a>
            <a className="ft-nav-link" href="#tariffs"><Icon>payments</Icon>Tariffs</a>
            <div className="ft-nav-contracts">
              <button className="ft-nav-link ft-nav-contract-button" type="button"><span><Icon>description</Icon>Contracts</span><Icon>expand_less</Icon></button>
              <div className="ft-contract-subnav"><a href="#add-contract"><i />Add Contract</a><a href="#view-contracts"><i />View Contracts</a></div>
            </div>
          </nav>
        </div>
        <div className="ft-nav-bottom">
          <div className="ft-connectivity"><div><span>System state</span><b>[Demo]</b></div><div><span>Integration state</span><b>[Demo]</b></div></div>
          <div className="ft-footer-nav"><a href="#status"><Icon>sensors</Icon>System Status</a><a href="#settings"><Icon>settings</Icon>Settings</a><button type="button">Collapse Menu <Icon>menu_open</Icon></button></div>
        </div>
      </aside>

      <div className="ft-main-frame">
        <header className="ft-topbar">
          <div className="ft-header-left"><div className="ft-crumb"><strong>FleetTrack</strong><span>/</span><span>Operations</span><span>/</span><b>Executive Overview</b></div><span className="ft-divider" /><button className="ft-branch" type="button"><Icon>storefront</Icon>Dubai Central Hub (DXB-01)<Icon>arrow_drop_down</Icon></button></div>
          <div className="ft-profile"><button className="ft-icon-button" type="button"><Icon>notifications</Icon><b>3</b></button><button className="ft-icon-button" type="button"><Icon>domain</Icon></button><span className="ft-divider" /><span className="ft-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span className="ft-user"><strong>{user.displayName}</strong><small>{user.userName}</small></span><button aria-label="Sign out" className="ft-logout" disabled={signingOut} onClick={signOut} type="button"><Icon>logout</Icon></button></div>
        </header>

        <main className="ft-dashboard">
          <section className="ft-title-row">
            <div><div className="ft-title"><h1>Operations Dashboard</h1><span className="ft-demo-pill"><i />DEMO DATA</span></div><p>Reference preview only — all metrics, contracts, alerts, and allocations below are <strong>[Demo]</strong> and not connected to live operations.</p></div>
            <div className="ft-actions"><button type="button"><Icon>file_download</Icon>Export Daily Log</button><button type="button"><Icon>person_add</Icon>+ Add Customer</button><button type="button"><Icon>directions_car</Icon>+ Add Vehicle</button><button className="ft-primary-action" type="button"><Icon>note_add</Icon>+ New Contract</button></div>
          </section>

          <section className="ft-metrics">
            <Metric title="Active Customers (Demo)" icon="group" value="1,428" footer={<><b className="ft-green">↗ +12 this week</b><span>38 Corporate</span></>} />
            <Metric title="Fleet Utilization (Demo)" icon="speed" value="91.8%" sub="312 / 340 Units" footer={<><b className="ft-amber">18 in Maintenance</b><b className="ft-green">10 Available</b></>} gauge />
            <Metric title="Open Agreements (Demo)" icon="assignment" value="248" footer={<><span>Active Contracts</span><b className="ft-red">⚠ 14 Overdue Today</b></>} />
            <Metric title="Receivables (Demo)" icon="account_balance_wallet" value="184,250" prefix="AED" footer={<><span>28 Invoices Due</span><b className="ft-amber">Salik/Fines: 14.3k</b></>} />
          </section>

          <section className="ft-content-grid">
            <section className="ft-panel ft-contracts-panel">
              <div className="ft-panel-toolbar"><div><Icon>sync_alt</Icon><h2>Recent Rental Contracts &amp; Handover Activity <small>(Demo)</small></h2></div><div><span>Filter by:</span><select aria-label="Filter contracts"><option>All Statuses (Demo)</option></select><button className="ft-refresh" type="button"><Icon>refresh</Icon></button></div></div>
              <div className="ft-table-wrap"><table><thead><tr><th>Agreement #</th><th>Customer Name</th><th>Vehicle (Plate / Model)</th><th>Out Date</th><th>Due Date</th><th>Daily Rate</th><th>Status</th><th>Actions</th></tr></thead><tbody>{contracts.map((contract) => <tr key={contract.agreement}><td className="ft-agreement">{contract.agreement}</td><td><strong>{contract.customer}</strong><small>{contract.detail}</small></td><td><span className="ft-plate">{contract.plate}</span><span className="ft-vehicle">{contract.vehicle}</span></td><td>{contract.out}</td><td className={contract.status === "Overdue" ? "ft-due-overdue" : ""}>{contract.due}{contract.status === "Overdue" && <small>2 DAYS OVERDUE</small>}</td><td className="ft-rate">{contract.rate}</td><td><Status status={contract.status} /></td><td><button className="ft-more" type="button"><Icon>more_vert</Icon></button></td></tr>)}</tbody></table></div>
              <div className="ft-table-footer"><span>Showing 10 of 248 agreements <strong>(Demo)</strong></span><div><button disabled type="button">Previous</button><button className="ft-page-current" type="button">1</button><button type="button">2</button><button type="button">3</button><button type="button">Next</button></div></div>
            </section>

            <aside className="ft-right-rail">
              <section className="ft-panel ft-alert-panel"><div className="ft-alert-title"><div><Icon>notification_important</Icon><h2>Fleet Health &amp; Alerts <small>(Demo)</small></h2></div><b>6 Critical</b></div>
                <article className="ft-alert"><div><strong><Icon>event_repeat</Icon>Registration Reminder <em>(Demo)</em></strong><b>Within 7 Days</b></div><p>[Demo] Example vehicle registration reminders for preview only. This does not use an RTA connection.</p><span>DXB-DEMO-01</span><span>DXB-DEMO-02</span><span>+2 more</span></article>
                <article className="ft-alert ft-alert-critical"><div><strong><Icon>fmd_bad</Icon>Overdue Returns <em>(Demo)</em></strong><b>Action Needed</b></div><p>[Demo] Example overdue-return alert. No vehicle tracking, Salik, or telemetry data is connected.</p><div><span>AGR-DEMO-9104, AGR-DEMO-8901</span><a href="#tracker">Open Tracker</a></div></article>
                <div className="ft-allocation"><h3>Branch Vehicle Allocation <small>(Demo)</small></h3><Allocation title="Sedan & Compact" value="140 units" width="45%" /><Allocation title="SUVs & 4x4" value="120 units" width="38%" secondary /><Allocation title="Commercial Vans & Pickups" value="50 units" width="17%" neutral /><div className="ft-telemetry">System state: <b>[Demo]</b><span>Hub Capacity: <b>310/350 [Demo]</b></span></div></div>
              </section>
              <section className="ft-workshop"><div><span><Icon>build</Icon></span><p><strong>Maintenance Workshop <em>(Demo)</em></strong><small>4 bays currently occupied [Demo]</small></p></div><button type="button">View Bay</button></section>
            </aside>
          </section>
        </main>
      </div>
    </div>
  );
}

function Metric({ title, icon, value, sub, prefix, footer, gauge = false }: { title: string; icon: string; value: string; sub?: string; prefix?: string; footer: React.ReactNode; gauge?: boolean }) {
  return <article className="ft-metric"><div className="ft-metric-label"><span>{title}</span><Icon>{icon}</Icon></div><div className="ft-metric-value">{prefix && <small>{prefix}</small>}<strong>{value}</strong>{sub && <span>{sub}</span>}</div>{gauge && <div className="ft-gauge"><i /><i /><i /></div>}<div className="ft-metric-footer">{footer}</div></article>;
}

function Allocation({ title, value, width, secondary, neutral }: { title: string; value: string; width: string; secondary?: boolean; neutral?: boolean }) {
  return <div className="ft-allocation-row"><div><span>{title}</span><b>{value} (Demo)</b></div><div className="ft-allocation-bar"><i className={secondary ? "secondary" : neutral ? "neutral" : ""} style={{ width }} /></div></div>;
}

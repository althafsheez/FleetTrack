"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const icons: Record<string, string> = {
  local_shipping: "▰", dashboard: "⊞", group: "♙", directions_car: "◆",
  payments: "¤", description: "▤", sensors: "◌", settings: "⚙", menu_open: "≪",
};

function Icon({ name }: { name: string }) {
  return <span aria-hidden className="material-symbols-outlined">{icons[name] ?? "•"}</span>;
}

const availablePages = [
  { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
  { href: "/customers", label: "Customers", icon: "group" },
  { href: "/vehicles", label: "Vehicles", icon: "directions_car" },
  { href: "/tariffs", label: "Tariffs", icon: "payments" },
];

export function FleetSidebar() {
  const pathname = usePathname();
  return <aside className="ft-sidenav">
    <div className="ft-nav-top">
      <div className="ft-brand"><div className="ft-brand-mark"><Icon name="local_shipping" /></div><div><div className="ft-brand-name">FleetTrack</div><div className="ft-brand-version">Enterprise Logistics v4.2</div></div></div>
      <nav className="ft-nav" aria-label="Main navigation">
        {availablePages.map((page) => <Link className={`ft-nav-link ${pathname === page.href ? "ft-nav-active" : ""}`} href={page.href} key={page.href}><Icon name={page.icon} />{page.label}</Link>)}
        <div>
          <Link className={`ft-nav-link ${pathname.startsWith("/contracts") ? "ft-nav-active" : ""}`} href="/contracts"><Icon name="description" />Contracts</Link>
          <div className="ft-contract-subnav" aria-label="Contract navigation">
            <Link className={pathname === "/contracts" ? "ft-subnav-active" : ""} href="/contracts"><i />Add Contract</Link>
            <Link className={pathname === "/contracts/list" ? "ft-subnav-active" : ""} href="/contracts/list"><i />Contract View</Link>
          </div>
        </div>
      </nav>
    </div>
    <div className="ft-nav-bottom"><div className="ft-connectivity"><div><span>System state</span><b>[Demo]</b></div><div><span>Integration state</span><b>[Demo]</b></div></div><div className="ft-footer-nav"><span><Icon name="sensors" />System Status</span><span><Icon name="settings" />Settings</span><button type="button"><span>Collapse Menu</span><Icon name="menu_open" /></button></div></div>
  </aside>;
}

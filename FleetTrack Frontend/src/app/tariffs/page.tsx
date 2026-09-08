"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createTariffGroup, getCurrentUser, getTariffGroup, getTariffGroups, logout, updateTariffGroup, type AuthenticatedUser, type TariffGroup, type TariffRates } from "@/lib/api";
import { FleetSidebar } from "@/components/fleet-sidebar";

const sections: { title: string; fields: [keyof TariffRates, string][] }[] = [
  { title: "Rental Rates", fields: [["DailyRate", "Daily Rate"], ["WeeklyRate", "Weekly Rate"], ["MonthlyRate", "Monthly Rate"]] },
  { title: "Discounts", fields: [["DiscountPercentPerDayDaily", "Discount % — Per Day"], ["DiscountPercent3DaysDaily", "Discount % — 3 Days"], ["DiscountPercent5DaysDaily", "Discount % — 5 Days"], ["DiscountPercentWeekly", "Discount % — Weekly"], ["DiscountPercentMonthly", "Discount % — Monthly"]] },
  { title: "Kilometres & Fuel", fields: [["AllowedKmsPerDay", "Allowed KM per Day"], ["ExtraKmCharges", "Extra KM Charge"], ["FuelCharges", "Fuel Charges"]] },
  { title: "Collision Damage Waiver (CDW)", fields: [["DailyCDW", "Daily CDW"], ["WeeklyCDW", "Weekly CDW"], ["MonthlyCDW", "Monthly CDW"]] },
  { title: "Personal Accident Insurance (PAI)", fields: [["DailyPAI", "Daily PAI"], ["WeeklyPAI", "Weekly PAI"], ["MonthlyPAI", "Monthly PAI"]] },
];

const blankRates = () => Object.fromEntries(sections.flatMap((section) => section.fields.map(([key]) => [key, "0.00"]))) as Record<string, string>;
const blankTariff = () => ({ TariffGroupId: 0, TariffGroupName: "", ...blankRates() } as TariffRates);

export default function TariffsPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [groups, setGroups] = useState<TariffGroup[]>([]);
  const [selected, setSelected] = useState<TariffRates | null>(null);
  const [drawer, setDrawer] = useState<"create" | "edit" | null>(null);
  const [draft, setDraft] = useState<TariffRates | null>(null);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const pageSize = 8;
  const totalPages = Math.max(1, Math.ceil(groups.length / pageSize));
  const visibleGroups = groups.slice((page - 1) * pageSize, page * pageSize);

  async function load(search = query, preferred?: number, resetPage = false) {
    setLoading(true);
    try {
      const rows = await getTariffGroups(search);
      setGroups(rows);
      const id = preferred ?? selected?.TariffGroupId;
      if (id && rows.some((group) => group.TariffGroupId === id)) setSelected(await getTariffGroup(id));
      else if (rows[0]) setSelected(await getTariffGroup(rows[0].TariffGroupId));
      else setSelected(null);
      const preferredIndex = preferred ? rows.findIndex((group) => group.TariffGroupId === preferred) : -1;
      setPage(preferredIndex >= 0 ? Math.floor(preferredIndex / pageSize) + 1 : resetPage ? 1 : (current) => Math.min(current, Math.max(1, Math.ceil(rows.length / pageSize))));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Tariff groups could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function initialise() {
      try {
        setUser(await getCurrentUser());
        await load("", undefined, true);
      } catch (cause) {
        if (cause instanceof Error && cause.message.includes("session")) router.replace("/login");
        else setError(cause instanceof Error ? cause.message : "FleetTrack could not be loaded.");
      }
    }
    void initialise();
  }, [router]);

  async function select(id: number) {
    setError(null);
    try {
      setSelected(await getTariffGroup(id));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Tariff detail could not be loaded.");
    }
  }

  function closeDrawer() {
    if (saving) return;
    setDrawer(null);
    setDraft(null);
  }

  function startCreate() {
    setError(null);
    setNotice(null);
    setDraft(blankTariff());
    setDrawer("create");
  }

  async function startEdit(id = selected?.TariffGroupId) {
    if (!id) return;
    setError(null);
    setNotice(null);
    try {
      setDraft(await getTariffGroup(id));
      setDrawer("edit");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Tariff detail could not be loaded.");
    }
  }

  async function save(form: HTMLFormElement) {
    if (!drawer || !draft) return;
    const data = new FormData(form);
    const name = String(data.get("TariffGroupName") ?? "").trim();
    if (!name) {
      setError("Tariff Group Name is required.");
      return;
    }
    const payload: Record<string, string> = { TariffGroupName: name };
    for (const section of sections) for (const [field] of section.fields) {
      const value = String(data.get(String(field)) ?? "").trim();
      if (!value || !/^\d+(\.\d{1,2})?$/.test(value)) {
        setError(`${String(field)} must be a non-negative amount with up to two decimals.`);
        return;
      }
      payload[String(field)] = value;
    }
    setSaving(true);
    setError(null);
    try {
      if (drawer === "create") {
        const created = await createTariffGroup(name);
        await updateTariffGroup(created.TariffGroupId, payload);
        setNotice(`Tariff group “${name}” created.`);
        await load(query, created.TariffGroupId);
      } else {
        const updated = await updateTariffGroup(draft.TariffGroupId, payload);
        setSelected(updated);
        setNotice("Tariff changes saved.");
        await load(query, draft.TariffGroupId);
      }
      setDrawer(null);
      setDraft(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Tariff group could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  if (!user) return <main className="ft-loading">Loading FleetTrack tariffs…</main>;

  return <div className="cu-app"><FleetSidebar /><div className="cu-frame">
    <header className="cu-topbar"><div className="cu-crumb"><b>FleetTrack</b><span>/</span><span>Operations</span><span>/</span><strong>Tariffs</strong></div><div className="cu-user"><span className="cu-avatar">{user.displayName.slice(0, 2).toUpperCase()}</span><span><b>{user.displayName}</b><small>{user.userName}</small></span><button className="cu-logout" onClick={() => { void logout().finally(() => router.replace("/login")); }} type="button">Logout</button></div></header>
    <main className="cu-main tf-main">
      <div className="cu-page-heading"><div><h1>Vehicle Tariffs</h1><p>Manage tariff groups and their rental rates and charges.</p></div><button className="cu-primary" onClick={startCreate} type="button">+ Create Tariff</button></div>
      {error && <p className="cu-api-error">{error}</p>}{notice && <p className="tf-notice">{notice}</p>}
      <div className="tf-workspace">
        <aside className="tf-groups"><div className="tf-group-tools"><b>Tariff Groups</b><div><input onChange={(event) => setQuery(event.target.value)} placeholder="Search tariff groups…" value={query} /><button onClick={() => { void load(query, undefined, true); }} type="button">Search</button></div></div><div className="tf-group-list">{loading ? <p>Loading tariff groups…</p> : visibleGroups.map((group) => <div className={selected?.TariffGroupId === group.TariffGroupId ? "tf-selected" : ""} key={group.TariffGroupId}><button onClick={() => { void select(group.TariffGroupId); }} type="button"><b>{group.TariffGroupName}</b><small>Group ID {group.TariffGroupId}</small></button><button className="tf-edit-row" onClick={() => { void startEdit(group.TariffGroupId); }} type="button">Edit</button></div>)}</div><footer className="tf-group-footer"><span>{groups.length} matching group{groups.length === 1 ? "" : "s"}</span>{totalPages > 1 && <div><button disabled={page === 1} onClick={() => setPage((current) => current - 1)} type="button">Previous</button>{Array.from({ length: totalPages }, (_, index) => index + 1).map((pageNumber) => <button aria-label={`Page ${pageNumber}`} className={pageNumber === page ? "tf-page-active" : ""} key={pageNumber} onClick={() => setPage(pageNumber)} type="button">{pageNumber}</button>)}<button disabled={page === totalPages} onClick={() => setPage((current) => current + 1)} type="button">Next</button></div>}</footer></aside>
        <section className="tf-detail">{selected ? <TariffDetail tariff={selected} onEdit={() => { void startEdit(); }} /> : <div className="tf-empty">Select a tariff group to view its details.</div>}</section>
      </div>
    </main>
  </div>{drawer && draft && <TariffDrawer key={`${drawer}-${draft.TariffGroupId}`} mode={drawer} saving={saving} tariff={draft} onClose={closeDrawer} onSave={save} />}</div>;
}

function TariffDetail({ tariff, onEdit }: { tariff: TariffRates; onEdit: () => void }) {
  return <div className="tf-detail-view"><header><div><small>TARIFF GROUP DETAIL</small><h2>{tariff.TariffGroupName}<em>Group ID {tariff.TariffGroupId}</em></h2></div><button className="cu-primary" onClick={onEdit} type="button">Edit Tariff</button></header><div className="tf-rates tf-readonly">{sections.map((section, index) => <section key={section.title}><h3>{index + 1}. {section.title}</h3><div>{section.fields.map(([field, label]) => <p key={String(field)}><small>{label}</small><b>{String(tariff[field] ?? "0.00")}</b></p>)}</div></section>)}</div></div>;
}

function TariffDrawer({ tariff, mode, saving, onClose, onSave }: { tariff: TariffRates; mode: "create" | "edit"; saving: boolean; onClose: () => void; onSave: (form: HTMLFormElement) => Promise<void> }) {
  const title = mode === "create" ? "Create Tariff" : "Edit Tariff";
  return <div className="cu-drawer-backdrop"><aside aria-label={title} className="cu-drawer tf-drawer"><header><div><small>{mode === "create" ? "NEW TARIFF GROUP" : "TARIFF GROUP"}</small><h2>{title}{mode === "edit" && <em>Group ID {tariff.TariffGroupId}</em>}</h2></div><button aria-label="Close tariff form" disabled={saving} onClick={onClose} type="button">×</button></header><div className="cu-drawer-content"><form className="tf-drawer-form" id="tariff-editor" onSubmit={(event) => { event.preventDefault(); void onSave(event.currentTarget); }}><section className="tf-group-name"><label>Tariff Group Name<input autoFocus defaultValue={tariff.TariffGroupName ?? ""} name="TariffGroupName" placeholder="e.g. Premium SUV" required /></label><p>This name identifies the rate group used by vehicles.</p></section><div className="tf-rates tf-editing">{sections.map((section, index) => <section key={section.title}><h3>{index + 1}. {section.title}</h3><div>{section.fields.map(([field, label]) => <label key={String(field)}>{label}<input defaultValue={String(tariff[field] ?? "0.00")} inputMode="decimal" name={String(field)} /></label>)}</div></section>)}</div></form></div><footer><button disabled={saving} onClick={onClose} type="button">Cancel</button><button className="cu-primary" disabled={saving} form="tariff-editor" type="submit">{saving ? "Saving…" : mode === "create" ? "Create Tariff" : "Save Changes"}</button><p>All values must be non-negative, with up to two decimal places.</p></footer></aside></div>;
}

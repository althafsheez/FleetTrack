export type AuthenticatedUser = {
  userId: number;
  userName: string;
  displayName: string;
};

type ErrorPayload = { detail?: unknown };

function getApiBaseUrl() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!apiUrl) throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  return apiUrl;
}

async function errorMessage(response: Response) {
  try {
    const body = (await response.json()) as ErrorPayload;
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // A safe generic message is returned below.
  }
  return response.status === 401
    ? "Invalid username or password. Please check your credentials and try again."
    : "We could not sign you in. Please try again.";
}

export async function login(username: string, password: string): Promise<AuthenticatedUser> {
  const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error(await errorMessage(response));
  return ((await response.json()) as { user: AuthenticatedUser }).user;
}

export async function getCurrentUser(): Promise<AuthenticatedUser> {
  const response = await fetch(`${getApiBaseUrl()}/auth/me`, { credentials: "include" });
  if (!response.ok) throw new Error("Your session has expired. Please sign in again.");
  return (await response.json()) as AuthenticatedUser;
}

export async function logout() {
  const response = await fetch(`${getApiBaseUrl()}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) throw new Error("We could not sign you out. Please try again.");
}

export type CustomerRecord = {
  ledgerId?: number;
  ledgerName?: string;
  ledgerNameInArabic?: string | null;
  openingBalance?: number | string | null;
  crOrDr?: string | null;
  emirateId?: number | null;
  mailingName?: string | null;
  bankAccountNumber?: string | null;
  branchName?: string | null;
  branchCode?: string | null;
  phone?: string | null;
  mobile?: string | null;
  email?: string | null;
  address?: string | null;
  creditPeriod?: number | null;
  creditLimit?: number | string | null;
  billByBill?: boolean | null;
  tin?: string | null;
  narration?: string | null;
  Nationality?: string | null;
  CustomerIdNo?: string | null;
  CustomerIdExpiry?: string | null;
  routeId?: number | null;
  areaId?: number | null;
  isCorporate?: boolean | null;
};

export type CustomerPayload = Omit<CustomerRecord, "ledgerId"> & {
  ledgerName: string;
  mobile: string;
  emirateId: number;
};

export type PaginatedCustomerResponse = {
  items: CustomerRecord[];
  total: number;
  offset: number;
  limit: number;
};

async function customerRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (response.ok) {
    if (response.status === 204) return undefined as T;
    return response.json() as Promise<T>;
  }
  if (response.status === 401) throw new Error("Your session has expired. Please sign in again.");
  try {
    const body = (await response.json()) as ErrorPayload;
    if (typeof body.detail === "string") throw new Error(body.detail);
    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((issue) => {
          if (!issue || typeof issue !== "object") return null;
          const detail = issue as { loc?: unknown; msg?: unknown };
          const field = Array.isArray(detail.loc) ? detail.loc.at(-1) : undefined;
          return typeof detail.msg === "string"
            ? `${typeof field === "string" ? field : "Field"}: ${detail.msg}`
            : null;
        })
        .filter((message): message is string => Boolean(message));
      if (messages.length) throw new Error(messages.join(" "));
    }
  } catch (error) {
    if (error instanceof Error && error.message !== "Unexpected end of JSON input") throw error;
  }
  throw new Error("The customer request could not be completed. Please try again.");
}

export function getCustomers() {
  return customerRequest<CustomerRecord[]>("/customers/");
}

export function getCustomer(customerId: number) {
  return customerRequest<CustomerRecord>(`/customers/${customerId}`);
}

export function searchCustomers(name?: string, mobile?: string) {
  const params = new URLSearchParams();
  if (name?.trim()) params.set("name", name.trim());
  if (mobile?.trim()) params.set("mobile", mobile.trim());
  return customerRequest<CustomerRecord[]>(`/customers/search?${params.toString()}`);
}

export function getCustomersPage(offset = 0, limit = 10) {
  return customerRequest<PaginatedCustomerResponse>(`/customers/page?offset=${offset}&limit=${limit}`);
}

export function searchCustomersPage(offset = 0, limit = 10, name?: string, mobile?: string) {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (name?.trim()) params.set("name", name.trim());
  if (mobile?.trim()) params.set("mobile", mobile.trim());
  return customerRequest<PaginatedCustomerResponse>(`/customers/search/page?${params.toString()}`);
}

export function createCustomer(payload: CustomerPayload) {
  return customerRequest<CustomerRecord>("/customers/", { method: "POST", body: JSON.stringify(payload) });
}

export function updateCustomer(customerId: number, payload: CustomerPayload) {
  return customerRequest<CustomerRecord>(`/customers/${customerId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export function deleteCustomer(customerId: number) {
  return customerRequest<void>(`/customers/${customerId}`, { method: "DELETE" });
}

export type VehicleRecord = {
  VehicleId: number; ModelId: number; EngineCapacityId: number; Year: number;
  PlateCodeId: number; PlateNo: string; RegistrationStartDate: string; RegistrationExpiryDate: string;
  InsurancePolicyId: number; InsurancePolicyRecNo: number; InsuranceExpDate: string;
  InsuranceCompanyId: number; InsuranceTypeId: number; TCNoId: number; TypeId: number;
  FuelCapacity: number; FuelCapacityUnitId: number; ChasisNo: string; EngineNo: string;
  TransmissionId: number; FuelTypeId: number; ColourId: number; SalikTag: string;
  InitialKmRdg: number; LatestKmRdg: number; TariffGroupId: number; StatusId: number;
  CreatedBy: number; CreatedDate: string; LastUpdatedBy: number; LastUpdatedDate: string;
  Remarks?: string | null; NextDueService?: number | null; AlertDate?: string | null;
  BranchId?: number | null; LocId?: number | null; FuelLevel?: number | null; VHType?: string | null;
};

export type VehiclePayload = Omit<VehicleRecord, "VehicleId" | "CreatedDate" | "LastUpdatedDate" | "CreatedBy" | "LastUpdatedBy"> & {
  CreatedBy?: number; LastUpdatedBy?: number;
};

export type PaginatedVehicleResponse = { items: VehicleRecord[]; total: number; offset: number; limit: number };
export type LookupRecord = Record<string, string | number | boolean | null>;

async function vehicleRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (response.ok) return response.json() as Promise<T>;
  if (response.status === 401) throw new Error("Your session has expired. Please sign in again.");
  try {
    const body = (await response.json()) as ErrorPayload;
    if (typeof body.detail === "string") throw new Error(body.detail);
    if (Array.isArray(body.detail)) {
      const message = body.detail.map((issue) => {
        if (!issue || typeof issue !== "object") return null;
        const value = issue as { loc?: unknown; msg?: unknown };
        const field = Array.isArray(value.loc) ? value.loc.at(-1) : "Field";
        return typeof value.msg === "string" ? `${String(field)}: ${value.msg}` : null;
      }).filter(Boolean).join(" ");
      if (message) throw new Error(message);
    }
  } catch (error) { if (error instanceof Error && error.message !== "Unexpected end of JSON input") throw error; }
  throw new Error("The vehicle request could not be completed. Please try again.");
}

export function getVehiclesPage(offset = 0, limit = 10, filters: { q?: string; plateNo?: string; fleetNo?: string } = {}) {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (filters.q?.trim()) params.set("q", filters.q.trim());
  if (filters.plateNo?.trim()) params.set("plate_no", filters.plateNo.trim());
  if (filters.fleetNo?.trim()) params.set("fleet_no", filters.fleetNo.trim());
  return vehicleRequest<PaginatedVehicleResponse>(`/vehicles/page?${params}`);
}

export function createVehicle(payload: VehiclePayload) {
  return vehicleRequest<VehicleRecord>("/vehicles/", { method: "POST", body: JSON.stringify(payload) });
}

export function updateVehicle(vehicleId: number, payload: Partial<VehiclePayload> & { LastUpdatedBy: number }) {
  return vehicleRequest<VehicleRecord>(`/vehicles/${vehicleId}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export function getLookup(path: string) {
  return vehicleRequest<LookupRecord[]>(`/lookups/${path}`);
}

export type TariffRates = {
  TariffGroupId: number;
  TariffGroupName?: string;
  DailyRate: string | number | null; WeeklyRate: string | number | null; MonthlyRate: string | number | null;
  DiscountPercentPerDayDaily: string | number | null; DiscountPercent3DaysDaily: string | number | null; DiscountPercent5DaysDaily: string | number | null;
  DiscountPercentWeekly: string | number | null; DiscountPercentMonthly: string | number | null;
  FuelCharges: string | number | null; AllowedKmsPerDay: string | number | null; ExtraKmCharges: string | number | null;
  DailyCDW: string | number | null; WeeklyCDW: string | number | null; MonthlyCDW: string | number | null;
  DailyPAI: string | number | null; WeeklyPAI: string | number | null; MonthlyPAI: string | number | null;
};
export type TariffGroup = { TariffGroupId: number; TariffGroupName: string };
export type ContractViewRow = { slNo: number; contractId: number; assignmentId?: number | null; agreementNo: string; customer: string; dateOut?: string | null; dateIn?: string | null; totalDays: number; rate: string | number; vehicleId?: number | null; vehicle?: string | null; rent: string | number; salik: string | number; fine: string | number; received: string | number; pendingAmount: string | number };
export type PaginatedContractView = { items: ContractViewRow[]; total: number; offset: number; limit: number };
export type ContractPayload = Record<string, string | number | boolean | null | undefined>;
export type ContractDetail = { contract: Record<string, string | number | boolean | null>; driver: Record<string, string | number | boolean | null> | null; vehicleAssignment: Record<string, string | number | boolean | null> | null };
export type ContractUpdate = Record<string, string | number | boolean | null | undefined>;

async function fleetRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, { credentials: "include", headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) }, ...init });
  if (response.ok) return response.json() as Promise<T>;
  if (response.status === 401) throw new Error("Your session has expired. Please sign in again.");
  try {
    const body = (await response.json()) as ErrorPayload;
    if (typeof body.detail === "string") throw new Error(body.detail);
    if (Array.isArray(body.detail)) {
      const messages = body.detail.map((entry) => {
        if (!entry || typeof entry !== "object") return null;
        const issue = entry as { loc?: unknown; msg?: unknown };
        const field = Array.isArray(issue.loc) ? issue.loc.at(-1) : "Field";
        return typeof issue.msg === "string" ? `${String(field)}: ${issue.msg}` : null;
      }).filter(Boolean);
      if (messages.length) throw new Error(messages.join(" "));
    }
  } catch (error) { if (error instanceof Error && error.message !== "Unexpected end of JSON input") throw error; }
  throw new Error("FleetTrack could not complete that request. Please try again.");
}

export function getTariffGroups(q?: string) { return fleetRequest<TariffGroup[]>(q?.trim() ? `/vehicle-tariff-groups/search?q=${encodeURIComponent(q.trim())}` : "/vehicle-tariff-groups/"); }
export function getTariffGroup(groupId: number) { return fleetRequest<TariffRates>(`/vehicle-tariff-groups/${groupId}`); }
export function createTariffGroup(TariffGroupName: string) { return fleetRequest<TariffGroup>("/vehicle-tariff-groups/", { method: "POST", body: JSON.stringify({ TariffGroupName }) }); }
export function updateTariffGroup(groupId: number, payload: Partial<TariffRates>) { return fleetRequest<TariffRates>(`/vehicle-tariff-groups/${groupId}`, { method: "PATCH", body: JSON.stringify(payload) }); }

export function getContractsPage(offset = 0, limit = 10, filters: { customerName?: string; agreementNo?: string; vehicle?: string } = {}) {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (filters.customerName?.trim()) params.set("customerName", filters.customerName.trim());
  if (filters.agreementNo?.trim()) params.set("agreementNo", filters.agreementNo.trim());
  if (filters.vehicle?.trim()) params.set("vehicle", filters.vehicle.trim());
  return fleetRequest<PaginatedContractView>(`/contracts/view/page?${params}`);
}
export function createContract(payload: ContractPayload) { return fleetRequest("/contracts/", { method: "POST", body: JSON.stringify(payload) }); }
export function getContract(contractId: number) { return fleetRequest<ContractDetail>(`/contracts/${contractId}`); }
export function getContractPrintPdfUrl(contractId: number, assignmentId: number) {
  return `${getApiBaseUrl()}/contracts/${contractId}/print.pdf?assignmentId=${assignmentId}`;
}
export function updateContract(contractId: number, payload: ContractUpdate) { return fleetRequest<ContractDetail>(`/contracts/${contractId}`, { method: "PATCH", body: JSON.stringify(payload) }); }

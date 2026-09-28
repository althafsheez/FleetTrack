const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type QueryValue = string | number | boolean | null | undefined;

export class ApiError extends Error {
  status: number;
  code?: string;
  ledgers: string[];
  canConfirm?: boolean;

  constructor(status: number, message: string, detail: { code?: string; ledgers?: string[]; canConfirm?: boolean } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = detail.code;
    this.ledgers = detail.ledgers ?? [];
    this.canConfirm = detail.canConfirm;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(init.headers ?? {}),
    },
  });
  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = typeof body === "object" && body && "detail" in body ? (body as { detail: unknown }).detail : body;
    const structured = typeof detail === "object" && detail !== null && !Array.isArray(detail)
      ? detail as { code?: unknown; message?: unknown; ledgers?: unknown; canConfirm?: unknown }
      : null;
    const message = Array.isArray(detail)
      ? detail.map((item) => typeof item === "object" && item && "msg" in item ? String(item.msg) : JSON.stringify(item)).join("; ")
      : structured?.message ? String(structured.message) : String(detail || `Request failed with status ${response.status}`);
    if (response.status === 401) throw new ApiError(response.status, `FleetTrack session expired. ${message}`);
    throw new ApiError(response.status, message, {
      code: typeof structured?.code === "string" ? structured.code : undefined,
      ledgers: Array.isArray(structured?.ledgers) ? structured.ledgers.map(String) : [],
      canConfirm: typeof structured?.canConfirm === "boolean" ? structured.canConfirm : undefined,
    });
  }
  return body as T;
}

function qs(params: Record<string, QueryValue>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value !== null && value !== undefined && value !== "") search.set(key, String(value));
  const text = search.toString();
  return text ? `?${text}` : "";
}

export type AuthenticatedUser = { userId: number; userName: string; displayName: string };
export type LookupRecord = Record<string, string | number | boolean | null | undefined>;
export type Page<T> = { items: T[]; total: number; offset: number; limit: number };

export type CustomerRecord = LookupRecord & {
  ledgerId: number; ledgerName: string; ledgerNameInArabic?: string | null; mobile?: string | null; email?: string | null;
  emirateId?: number | null; CustomerIdNo?: string | null; CustomerIdExpiry?: string | null; creditLimit?: number | string | null; isCorporate?: boolean | null;
};
export type CustomerPayload = Record<string, string | number | boolean | null>;

export type VehicleRecord = LookupRecord & {
  VehicleId: number; ModelId: number; EngineCapacityId: number; Year: number; PlateCodeId: number; PlateNo: string; VHType?: string | null;
  RegistrationStartDate: string; RegistrationExpiryDate: string; InsurancePolicyId: number; InsurancePolicyRecNo?: number | null; InsuranceExpDate: string;
  InsuranceCompanyId: number; InsuranceTypeId: number; TCNoId: number; TypeId: number; FuelCapacity: number; FuelCapacityUnitId: number;
  ChasisNo: string; EngineNo: string; TransmissionId: number; FuelTypeId: number; ColourId: number; SalikTag: string;
  InitialKmRdg: number; LatestKmRdg: number; TariffGroupId: number; StatusId: number; Remarks?: string | null;
  NextDueService?: number | null; AlertDate?: string | null; BranchId?: number | null; LocId?: number | null; FuelLevel?: number | null;
};
export type VehiclePayload = Record<string, string | number | boolean | null>;

export type TariffGroup = { TariffGroupId: number; TariffGroupName: string };
export type TariffRates = TariffGroup & Record<string, string | number | null>;

export type ContractPayload = Record<string, string | number | boolean | null | undefined | RentalInvoiceSettings>;
export type ContractUpdate = Record<string, string | number | boolean | null | undefined>;
export type ContractViewRow = {
  slNo: number; contractId: number; assignmentId?: number | null; agreementNo: string; customer: string; dateOut?: string | null; dateIn?: string | null;
  totalDays: number; rate: string | number; vehicleId?: number | null; vehicle?: string | null; rent: string | number; salik: string | number;
  fine: string | number; received: string | number; pendingAmount: string | number;
};
export type ContractDetail = { contract: LookupRecord; driver?: LookupRecord | null; vehicleAssignment?: LookupRecord | null };

export type RentalInvoiceSettings = { salesAccountId: number; exchangeRateId: number; creditPeriod: number; lpoNo?: string | null };
export type RentalInvoiceDueRow = {
  contractId: number; contractRefNo: string; customerId?: number | null; customerName?: string | null; contractType: number;
  paymentType: number; billingType?: number | null; nextInvoiceDate: string;
};
export type RentalInvoicePreview = {
  contractId: number; contractRefNo: string; invoiceDate: string; periodStart: string; periodEnd: string; nextInvoiceDate: string;
  taxAmount: string | number; totalAmount: string | number; grandTotal: string | number; narration: string; lines: RentalInvoiceLinePreview[];
};
export type RentalInvoiceLinePreview = {
  itemTypeId: number; itemTypeName: string; vehicleId: number; description: string; quantity: string | number; unitId: number;
  rate: string | number; taxId: number; taxAmount: string | number; amount: string | number;
};
export type SalesInvoiceRegisterRow = {
  salesMasterId: number; invoiceType: "rental" | "salik" | "fine" | "misc" | "vehicle"; voucherTypeId: number; voucherNo?: string | null;
  invoiceNo?: string | null; invoiceDate?: string | null; customerName?: string | null; contractRefNo?: string | null; vehicleNos?: string | null;
  grandTotal: string | number; isPosted?: boolean | null;
};
export type SalesInvoiceResponse = SalesInvoiceRegisterRow & {
  customerId?: number | null; contractId?: number | null; creditPeriod: number; lpoNo?: string | null; salesAccountId?: number | null;
  salesAccountName?: string | null; exchangeRateId?: number | null; locationName?: string | null; taxAmount: string | number;
  billDiscount: string | number; totalAmount: string | number; narration?: string | null; lines: RentalInvoiceLinePreview[];
};
export type InvoiceLookup = { id: number; name: string; taxId?: number | null; taxRate?: string | number | null; rate?: string | number | null; currencyId?: number | null; currencyName?: string | null; currencySymbol?: string | null };

export type ContraDirection = "deposit" | "withdrawal";
export type ContraAccount = { id: number; name: string; accountGroupId?: number | null; accountGroupName?: string | null; isBank: boolean };
export type ContraExchangeRate = { id: number; currencyId: number; currencyName?: string | null; currencySymbol?: string | null; rate: string | number; date?: string | null };
export type ContraNumberingRule = {
  voucherTypeId: number; numberingMethod: string; automatic: boolean; suffixPrefixId: number; prefix?: string | null; suffix?: string | null;
  startIndex?: number | null; widthOfNumericalPart?: number | null; prefillWithZero?: boolean | null; nextVoucherNo?: string | null;
  nextInvoiceNo?: string | null; fromDate?: string | null; toDate?: string | null;
};
export type ContraVoucherLineInput = {
  contraDetailsId?: number | null; ledgerId: number; amount: string; exchangeRateId: number; chequeNo?: string | null; chequeDate?: string | null;
};
export type ContraVoucherPayload = {
  voucherDate: string; direction: ContraDirection; headerLedgerId: number; manualVoucherNo?: string | null; narration?: string | null;
  idempotencyKey?: string | null; confirmNegativeBalance: boolean; lines: ContraVoucherLineInput[];
};
export type ContraVoucherLine = ContraVoucherLineInput & {
  contraDetailsId: number; ledgerName?: string | null; exchangeRate: string | number; currencyId?: number | null; currencyName?: string | null;
  currencySymbol?: string | null; baseAmount: string | number;
};
export type ContraVoucherRegisterRow = {
  contraMasterId: number; voucherNo: string; invoiceNo: string; voucherDate: string; direction: ContraDirection; headerLedgerId: number;
  headerLedgerName?: string | null; offsetAccountNames: string[]; lineCount: number; totalAmount: string | number; narration?: string | null;
};
export type ContraVoucherResponse = ContraVoucherRegisterRow & {
  voucherTypeId: number; suffixPrefixId: number; idempotencyKey?: string | null; userId: number; financialYearId: number; lines: ContraVoucherLine[];
};
export type ContraRegisterFilters = { fromDate?: string; toDate?: string; voucherNo?: string; ledgerId?: number | ""; direction?: ContraDirection | "" };

export type PaymentReferenceType = "against" | "new" | "on_account";
export type PaymentVoucherType = { id: number; name: string; numberingMethod?: string | null };
export type PaymentAccount = { id: number; name: string; accountGroupId?: number | null; accountGroupName?: string | null };
export type PaymentDetailAccount = PaymentAccount & { billByBill: boolean };
export type PaymentExchangeRate = { id: number; currencyId: number; currencyName?: string | null; currencySymbol?: string | null; rate: string | number; date?: string | null };
export type PaymentVehicle = { id: number; plateNo: string };
export type PaymentNumberingRule = ContraNumberingRule;
export type OpenPaymentReference = {
  ledgerId: number; sourceVoucherTypeId: number; sourceVoucherTypeName?: string | null; sourceVoucherNo: string;
  sourceInvoiceNo?: string | null; pendingAmount: string | number; exchangeRateId: number; exchangeRate: string | number;
  currencyId?: number | null; currencyName?: string | null; currencySymbol?: string | null; contractId?: number | null;
};
export type PaymentAllocationInput = {
  partyBalanceId?: number | null; referenceType: PaymentReferenceType; sourceVoucherTypeId?: number | null;
  sourceVoucherNo?: string | null; amount: string;
};
export type PaymentAllocation = PaymentAllocationInput & {
  partyBalanceId: number; sourceVoucherTypeName?: string | null; sourceInvoiceNo?: string | null; exchangeRateId: number;
  exchangeRate: string | number; currencyId?: number | null; contractId?: number | null;
};
export type PaymentVoucherLineInput = {
  paymentDetailsId?: number | null; ledgerId: number; amount: string; exchangeRateId: number; chequeNo?: string | null;
  chequeDate?: string | null; vehicleId?: number | null; allocations: PaymentAllocationInput[];
};
export type PaymentVoucherPayload = {
  voucherTypeId: number; voucherDate: string; payingLedgerId: number; manualVoucherNo?: string | null; narration?: string | null;
  idempotencyKey?: string | null; lines: PaymentVoucherLineInput[];
};
export type PaymentVoucherLine = Omit<PaymentVoucherLineInput, "allocations"> & {
  paymentDetailsId: number; ledgerName?: string | null; exchangeRate: string | number; currencyId?: number | null;
  currencyName?: string | null; currencySymbol?: string | null; baseAmount: string | number; vehicleNo?: string | null;
  billByBill: boolean; allocations: PaymentAllocation[];
};
export type PaymentVoucherRegisterRow = {
  paymentMasterId: number; voucherNo: string; invoiceNo: string; voucherTypeId: number; voucherTypeName?: string | null;
  voucherDate: string; payingLedgerId: number; payingLedgerName?: string | null; totalAmount: string | number;
  narration?: string | null; isPosted: boolean; detailAccountNames: string[]; lineCount: number;
};
export type PaymentVoucherResponse = PaymentVoucherRegisterRow & {
  suffixPrefixId: number; idempotencyKey?: string | null; userId: number; financialYearId: number; lines: PaymentVoucherLine[];
};
export type PaymentRegisterFilters = {
  fromDate?: string; toDate?: string; voucherNo?: string; voucherTypeId?: number | ""; payingLedgerId?: number | "";
  amount?: string; partyLedgerId?: number | ""; chequeNo?: string; posted?: boolean | "";
};

export type ReceiptReferenceType = "against" | "on_account";
export type ReceiptVoucherType = { id: number; name: string; numberingMethod?: string | null };
export type ReceiptAccount = { id: number; name: string; accountGroupId?: number | null; accountGroupName?: string | null };
export type ReceiptDetailAccount = ReceiptAccount & { billByBill: boolean };
export type ReceiptExchangeRate = PaymentExchangeRate;
export type ReceiptNumberingRule = ContraNumberingRule;
export type ReceiptContract = { id: number; contractRefNo: string };
export type OpenReceiptReference = {
  ledgerId: number; sourceVoucherTypeId: number; sourceVoucherTypeName?: string | null; sourceVoucherNo: string;
  sourceInvoiceNo?: string | null; pendingAmount: string | number; exchangeRateId: number; exchangeRate: string | number;
  currencyId?: number | null; currencyName?: string | null; currencySymbol?: string | null; contractId?: number | null;
};
export type ReceiptAllocationInput = {
  partyBalanceId?: number | null; referenceType: ReceiptReferenceType; sourceVoucherTypeId?: number | null;
  sourceVoucherNo?: string | null; contractId?: number | null; amount: string;
};
export type ReceiptAllocation = ReceiptAllocationInput & {
  partyBalanceId: number; sourceVoucherTypeName?: string | null; sourceInvoiceNo?: string | null; exchangeRateId: number;
  exchangeRate: string | number; currencyId?: number | null;
};
export type ReceiptVoucherLineInput = {
  receiptDetailsId?: number | null; ledgerId: number; amount: string; exchangeRateId: number; chequeNo?: string | null;
  chequeDate?: string | null; allocations: ReceiptAllocationInput[];
};
export type ReceiptVoucherPayload = {
  voucherTypeId: number; voucherDate: string; receivingLedgerId: number; manualVoucherNo?: string | null; narration?: string | null;
  idempotencyKey?: string | null; lines: ReceiptVoucherLineInput[];
};
export type ReceiptVoucherLine = Omit<ReceiptVoucherLineInput, "allocations"> & {
  receiptDetailsId: number; ledgerName?: string | null; exchangeRate: string | number; currencyId?: number | null;
  currencyName?: string | null; currencySymbol?: string | null; baseAmount: string | number;
  billByBill: boolean; allocations: ReceiptAllocation[];
};
export type ReceiptVoucherRegisterRow = {
  receiptMasterId: number; voucherNo: string; invoiceNo: string; voucherTypeId: number; voucherTypeName?: string | null;
  voucherDate: string; receivingLedgerId: number; receivingLedgerName?: string | null; totalAmount: string | number;
  narration?: string | null; isPosted: boolean; detailAccountNames?: string[]; lineCount?: number;
};
export type ReceiptVoucherResponse = ReceiptVoucherRegisterRow & {
  suffixPrefixId: number; idempotencyKey?: string | null; userId: number; financialYearId: number; lines: ReceiptVoucherLine[];
};
export type ReceiptRegisterFilters = {
  fromDate?: string; toDate?: string; voucherNo?: string; voucherTypeId?: number | ""; receivingLedgerId?: number | "";
  amount?: string; partyLedgerId?: number | ""; chequeNo?: string; posted?: boolean | "";
};

export async function login(username: string, password: string) {
  return request<{ user: AuthenticatedUser }>("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
}
export async function logout() { return request<void>("/auth/logout", { method: "POST" }); }
export async function getCurrentUser() { return request<AuthenticatedUser>("/auth/me"); }

export async function getLookup(path: string) { return request<LookupRecord[]>(`/lookups/${path}`); }
export async function getCustomersPage(offset = 0, limit = 10) { return request<Page<CustomerRecord>>(`/customers/page${qs({ offset, limit })}`); }
export async function searchCustomersPage(offset = 0, limit = 10, name?: string, mobile?: string) { return request<Page<CustomerRecord>>(`/customers/search/page${qs({ offset, limit, name, mobile })}`); }
export async function createCustomer(payload: CustomerPayload) { return request<CustomerRecord>("/customers/", { method: "POST", body: JSON.stringify(payload) }); }
export async function updateCustomer(id: number, payload: CustomerPayload) { return request<CustomerRecord>(`/customers/${id}`, { method: "PUT", body: JSON.stringify(payload) }); }

export async function getVehiclesPage(offset = 0, limit = 10, filters: { q?: string; plateNo?: string; fleetNo?: string } = {}) {
  return request<Page<VehicleRecord>>(`/vehicles/page${qs({ offset, limit, q: filters.q, plate_no: filters.plateNo, fleet_no: filters.fleetNo })}`);
}
export async function createVehicle(payload: VehiclePayload) { return request<VehicleRecord>("/vehicles/", { method: "POST", body: JSON.stringify(payload) }); }
export async function updateVehicle(id: number, payload: VehiclePayload) { return request<VehicleRecord>(`/vehicles/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); }

export async function getTariffGroups(q = "") { return request<TariffGroup[]>(q ? `/vehicle-tariff-groups/search${qs({ q })}` : "/vehicle-tariff-groups/"); }
export async function getTariffGroup(id: number) { return request<TariffRates>(`/vehicle-tariff-groups/${id}`); }
export async function createTariffGroup(name: string) { return request<TariffGroup>("/vehicle-tariff-groups/", { method: "POST", body: JSON.stringify({ TariffGroupName: name }) }); }
export async function updateTariffGroup(id: number, payload: Record<string, string | number | null>) { return request<TariffRates>(`/vehicle-tariff-groups/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); }

export async function createContract(payload: ContractPayload) { return request<ContractDetail>("/contracts/", { method: "POST", body: JSON.stringify(payload) }); }
export async function getContractsPage(offset = 0, limit = 10, filters: { customerName?: string; agreementNo?: string; vehicle?: string } = {}) {
  return request<Page<ContractViewRow>>(`/contracts/view/page${qs({ offset, limit, ...filters })}`);
}
export async function getContract(id: number) { return request<ContractDetail>(`/contracts/${id}`); }
export async function updateContract(id: number, payload: ContractUpdate) { return request<ContractDetail>(`/contracts/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); }

export async function getInvoiceLookup(name: string, params: Record<string, QueryValue> = {}) {
  return request<InvoiceLookup[]>(`/sales-invoices/lookups/${name}${qs(params)}`);
}
export async function getDueRentalInvoices(asOfDate?: string) { return request<RentalInvoiceDueRow[]>(`/rental-invoices/due${qs({ asOfDate })}`); }
export async function previewRentalInvoice(contractId: number, payload: RentalInvoiceSettings & { asOfDate?: string | null }) {
  return request<RentalInvoicePreview>(`/contracts/${contractId}/rental-invoices/preview`, { method: "POST", body: JSON.stringify(payload) });
}
export async function createRentalInvoice(contractId: number, payload: RentalInvoiceSettings & { asOfDate?: string | null }) {
  return request<SalesInvoiceResponse>(`/contracts/${contractId}/rental-invoices`, { method: "POST", body: JSON.stringify(payload) });
}
export async function deleteRentalInvoice(contractId: number, salesMasterId: number) {
  return request<void>(`/contracts/${contractId}/rental-invoices/${salesMasterId}`, { method: "DELETE" });
}
export async function getSalesInvoicesPage(offset = 0, limit = 10, filters: { q?: string; invoiceType?: string; posted?: boolean | "" } = {}) {
  return request<Page<SalesInvoiceRegisterRow>>(`/sales-invoices/page${qs({ offset, limit, q: filters.q, invoiceType: filters.invoiceType, posted: filters.posted })}`);
}

export async function getContraVouchersPage(offset = 0, limit = 25, filters: ContraRegisterFilters = {}) {
  return request<Page<ContraVoucherRegisterRow>>(`/contra-vouchers/page${qs({ offset, limit, ...filters })}`);
}
export async function getContraVoucher(id: number) { return request<ContraVoucherResponse>(`/contra-vouchers/${id}`); }
export async function getContraAccounts() { return request<ContraAccount[]>("/contra-vouchers/lookups/accounts"); }
export async function getContraExchangeRates(voucherDate: string) {
  return request<ContraExchangeRate[]>(`/contra-vouchers/lookups/exchange-rates${qs({ date: `${voucherDate}T00:00:00` })}`);
}
export async function getContraNumberingRule(voucherDate: string) {
  return request<ContraNumberingRule>(`/contra-vouchers/lookups/numbering-rule${qs({ date: `${voucherDate}T00:00:00` })}`);
}
export async function createContraVoucher(payload: ContraVoucherPayload) {
  return request<ContraVoucherResponse>("/contra-vouchers/", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateContraVoucher(id: number, payload: ContraVoucherPayload) {
  return request<ContraVoucherResponse>(`/contra-vouchers/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function deleteContraVoucher(id: number) { return request<void>(`/contra-vouchers/${id}`, { method: "DELETE" }); }
export async function getContraPrintData(id: number) { return request<ContraVoucherResponse>(`/contra-vouchers/${id}/print-data`); }

export async function getPaymentVouchersPage(offset = 0, limit = 25, filters: PaymentRegisterFilters = {}) {
  const dates = {
    fromDate: filters.fromDate ? `${filters.fromDate}T00:00:00` : undefined,
    toDate: filters.toDate ? `${filters.toDate}T00:00:00` : undefined,
  };
  return request<Page<PaymentVoucherRegisterRow>>(`/payment-vouchers/page${qs({ offset, limit, ...filters, ...dates })}`);
}
export async function getPaymentVoucher(id: number) { return request<PaymentVoucherResponse>(`/payment-vouchers/${id}`); }
export async function getPaymentVoucherTypes() { return request<PaymentVoucherType[]>("/payment-vouchers/lookups/voucher-types"); }
export async function getPaymentPayingAccounts() { return request<PaymentAccount[]>("/payment-vouchers/lookups/paying-accounts"); }
export async function getPaymentDetailAccounts(search = "", limit = 200) { return request<PaymentDetailAccount[]>(`/payment-vouchers/lookups/detail-accounts${qs({ search, limit })}`); }
export async function getPaymentPartyLedgers(search = "", limit = 200) { return request<PaymentDetailAccount[]>(`/payment-vouchers/lookups/party-ledgers${qs({ search, limit })}`); }
export async function getPaymentExchangeRates(voucherDate: string) { return request<PaymentExchangeRate[]>(`/payment-vouchers/lookups/exchange-rates${qs({ date: `${voucherDate}T00:00:00` })}`); }
export async function getPaymentVehicles(search = "", limit = 200) { return request<PaymentVehicle[]>(`/payment-vouchers/lookups/vehicles${qs({ search, limit })}`); }
export async function getPaymentNumberingRule(voucherTypeId: number, voucherDate: string) { return request<PaymentNumberingRule>(`/payment-vouchers/lookups/numbering-rule${qs({ voucherTypeId, date: `${voucherDate}T00:00:00` })}`); }
export async function getPaymentOpenReferences(ledgerId: number) { return request<OpenPaymentReference[]>(`/payment-vouchers/party-ledgers/${ledgerId}/open-references`); }
export async function createPaymentVoucher(payload: PaymentVoucherPayload) { return request<PaymentVoucherResponse>("/payment-vouchers/", { method: "POST", body: JSON.stringify(payload) }); }
export async function updatePaymentVoucher(id: number, payload: PaymentVoucherPayload) { return request<PaymentVoucherResponse>(`/payment-vouchers/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); }
export async function deletePaymentVoucher(id: number) { return request<void>(`/payment-vouchers/${id}`, { method: "DELETE" }); }
export async function postPaymentVoucher(id: number) { return request<PaymentVoucherResponse>(`/payment-vouchers/${id}/post`, { method: "POST" }); }
export async function unpostPaymentVoucher(id: number) { return request<PaymentVoucherResponse>(`/payment-vouchers/${id}/unpost`, { method: "POST" }); }
export async function getPaymentPrintData(id: number) { return request<PaymentVoucherResponse>(`/payment-vouchers/${id}/print-data`); }

export async function getReceiptVouchersPage(offset = 0, limit = 25, filters: ReceiptRegisterFilters = {}) {
  const dates = {
    fromDate: filters.fromDate ? `${filters.fromDate}T00:00:00` : undefined,
    toDate: filters.toDate ? `${filters.toDate}T00:00:00` : undefined,
  };
  return request<Page<ReceiptVoucherRegisterRow>>(`/receipt-vouchers/page${qs({ offset, limit, ...filters, ...dates })}`);
}
export async function getReceiptVoucher(id: number) { return request<ReceiptVoucherResponse>(`/receipt-vouchers/${id}`); }
export async function getReceiptVoucherTypes() { return request<ReceiptVoucherType[]>("/receipt-vouchers/lookups/voucher-types"); }
export async function getReceiptReceivingAccounts() { return request<ReceiptAccount[]>("/receipt-vouchers/lookups/receiving-accounts"); }
export async function getReceiptDetailAccounts(search = "", limit = 200) { return request<ReceiptDetailAccount[]>(`/receipt-vouchers/lookups/detail-accounts${qs({ search, limit })}`); }
export async function getReceiptPartyLedgers(search = "", limit = 200) { return request<ReceiptDetailAccount[]>(`/receipt-vouchers/lookups/party-ledgers${qs({ search, limit })}`); }
export async function getReceiptExchangeRates(voucherDate: string) { return request<ReceiptExchangeRate[]>(`/receipt-vouchers/lookups/exchange-rates${qs({ date: `${voucherDate}T00:00:00` })}`); }
export async function getReceiptNumberingRule(voucherTypeId: number, voucherDate: string) { return request<ReceiptNumberingRule>(`/receipt-vouchers/lookups/numbering-rule${qs({ voucherTypeId, date: `${voucherDate}T00:00:00` })}`); }
export async function getReceiptOpenReferences(ledgerId: number) { return request<OpenReceiptReference[]>(`/receipt-vouchers/party-ledgers/${ledgerId}/open-references`); }
export async function getReceiptPartyContracts(ledgerId: number) { return request<ReceiptContract[]>(`/receipt-vouchers/party-ledgers/${ledgerId}/contracts`); }
export async function createReceiptVoucher(payload: ReceiptVoucherPayload) { return request<ReceiptVoucherResponse>("/receipt-vouchers/", { method: "POST", body: JSON.stringify(payload) }); }
export async function updateReceiptVoucher(id: number, payload: ReceiptVoucherPayload) { return request<ReceiptVoucherResponse>(`/receipt-vouchers/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); }
export async function deleteReceiptVoucher(id: number) { return request<void>(`/receipt-vouchers/${id}`, { method: "DELETE" }); }
export async function postReceiptVoucher(id: number) { return request<ReceiptVoucherResponse>(`/receipt-vouchers/${id}/post`, { method: "POST" }); }
export async function unpostReceiptVoucher(id: number) { return request<ReceiptVoucherResponse>(`/receipt-vouchers/${id}/unpost`, { method: "POST" }); }
export async function getReceiptPrintData(id: number) { return request<ReceiptVoucherResponse>(`/receipt-vouchers/${id}/print-data`); }

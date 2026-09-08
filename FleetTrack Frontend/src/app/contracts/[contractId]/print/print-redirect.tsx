"use client";

import Link from "next/link";
import { useEffect, useMemo } from "react";
import { getContractPrintPdfUrl } from "@/lib/api";

export function ContractPrintRedirect({ contractId, assignmentId }: { contractId: number; assignmentId: number }) {
  const valid = Number.isInteger(contractId) && contractId > 0 && Number.isInteger(assignmentId) && assignmentId > 0;
  const pdfUrl = useMemo(
    () => (valid ? getContractPrintPdfUrl(contractId, assignmentId) : null),
    [assignmentId, contractId, valid],
  );

  useEffect(() => {
    if (pdfUrl) window.location.replace(pdfUrl);
  }, [pdfUrl]);

  if (!valid) {
    return <main style={{ minHeight: "100vh", display: "grid", placeContent: "center", textAlign: "center", fontFamily: "Arial, sans-serif" }}>
      <h1>Unable to prepare contract</h1>
      <p>A valid contract and vehicle assignment are required for printing.</p>
      <Link href="/contracts/list">Return to Contract View</Link>
    </main>;
  }

  return <main style={{ minHeight: "100vh", display: "grid", placeContent: "center", fontFamily: "Arial, sans-serif" }}>
    <p>Preparing the original rental agreement PDF…</p>
  </main>;
}

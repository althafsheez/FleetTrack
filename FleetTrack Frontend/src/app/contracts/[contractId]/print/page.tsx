import { ContractPrintRedirect } from "./print-redirect";

export default async function ContractPrintPage({
  params,
  searchParams,
}: {
  params: Promise<{ contractId: string }>;
  searchParams: Promise<{ assignmentId?: string }>;
}) {
  const [{ contractId }, query] = await Promise.all([params, searchParams]);
  return <ContractPrintRedirect assignmentId={Number(query.assignmentId)} contractId={Number(contractId)} />;
}

"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

const capabilities = [
  ["Customer management", "Maintain customer contact, identification, and credit information."],
  ["Vehicle management", "Manage vehicle registration, insurance, technical, and operational information."],
  ["Tariff management", "Configure daily, weekly, and monthly rental rates and related charges."],
  ["Contract management", "Create rental agreements and review contract and payment information."],
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(username.trim(), password);
      router.replace("/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We could not sign you in. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="dot-grid relative flex min-h-screen flex-col overflow-hidden bg-slate-50 text-slate-900">
      <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-[radial-gradient(ellipse_at_top,_rgba(219,234,254,.8),_transparent_65%)]" />
      <header className="relative flex h-16 items-center border-b border-slate-200/80 bg-white/80 px-5 backdrop-blur sm:px-10">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-slate-900 text-sm font-bold text-white">FT</div>
          <span className="text-lg font-bold tracking-tight">FleetTrack</span>
          <span className="hidden h-5 border-l border-slate-300 sm:block" />
          <span className="hidden font-mono text-xs text-slate-500 sm:block">Fleet and rental management</span>
        </div>
      </header>

      <section className="relative mx-auto flex w-full max-w-6xl flex-1 items-center px-4 py-10 sm:px-6 lg:px-10">
        <div className="grid w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_20px_50px_-12px_rgba(15,23,42,.16)] lg:grid-cols-12">
          <section className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8 text-white sm:p-10 lg:col-span-5">
            <div aria-hidden className="absolute inset-0 opacity-20 [background-image:radial-gradient(#93c5fd_1px,transparent_1px)] [background-size:20px_20px]" />
            <div className="relative">
              <span className="inline-flex rounded-md border border-white/15 bg-white/10 px-3 py-1 font-mono text-[11px] uppercase tracking-wide text-blue-100">Fleet management platform</span>
              <h1 className="mt-7 text-3xl font-bold leading-tight tracking-tight">Fleet and Rental Management, Simplified.</h1>
              <p className="mt-4 max-w-md text-sm leading-6 text-slate-300">FleetTrack brings customer records, vehicle information, tariff management, and rental contracts together in one organized workspace.</p>
              <div className="mt-8 space-y-3">
                {capabilities.map(([title, description], index) => (
                  <article className="flex gap-3 rounded-xl border border-white/10 bg-white/5 p-3" key={title}>
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-blue-300/20 bg-blue-400/15 font-mono text-xs text-blue-200">0{index + 1}</span>
                    <div><h2 className="text-sm font-semibold">{title}</h2><p className="mt-1 text-xs leading-5 text-slate-300">{description}</p></div>
                  </article>
                ))}
              </div>
              <p className="mt-8 border-t border-white/10 pt-5 text-sm italic text-slate-300">“From customer registration to rental agreement—all in one place.”</p>
            </div>
          </section>

          <section className="p-8 sm:p-12 lg:col-span-7 lg:p-14">
            <div className="mx-auto flex h-full max-w-md flex-col justify-center">
              <div className="mb-8"><div className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-slate-100 text-lg">⌁</div><h2 className="mt-4 text-2xl font-bold tracking-tight">Welcome to FleetTrack</h2><p className="mt-2 text-sm leading-6 text-slate-500">Sign in to manage customers, vehicles, tariffs, and rental contracts.</p></div>
              {error ? <div role="alert" className="mb-6 flex items-start justify-between gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"><span>{error}</span><button aria-label="Dismiss error" className="text-rose-500 hover:text-rose-800" onClick={() => setError(null)} type="button">×</button></div> : null}
              <form className="space-y-5" onSubmit={onSubmit}>
                <label className="block text-sm font-medium text-slate-700">Username<input autoComplete="username" className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-slate-900 focus:bg-white focus:ring-2 focus:ring-slate-900/15" onChange={(event) => setUsername(event.target.value)} placeholder="Enter your username" required value={username} /></label>
                <label className="block text-sm font-medium text-slate-700">Password<span className="relative mt-2 block"><input autoComplete="current-password" className="h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 pr-14 text-sm outline-none transition placeholder:text-slate-400 focus:border-slate-900 focus:bg-white focus:ring-2 focus:ring-slate-900/15" onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required type={showPassword ? "text" : "password"} value={password} /><button className="absolute inset-y-0 right-0 px-4 text-xs font-medium text-slate-500 hover:text-slate-900" onClick={() => setShowPassword((visible) => !visible)} type="button">{showPassword ? "Hide" : "Show"}</button></span></label>
                <button className="flex h-11 w-full items-center justify-center rounded-xl bg-slate-900 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60" disabled={isSubmitting} type="submit">{isSubmitting ? "Signing in…" : "Sign in →"}</button>
              </form>
              <p className="mt-10 border-t border-slate-100 pt-6 text-xs text-slate-400">Authorized FleetTrack personnel only.</p>
            </div>
          </section>
        </div>
      </section>
      <footer className="relative border-t border-slate-200/80 bg-white/80 px-5 py-4 text-xs text-slate-500 sm:px-10">© {new Date().getFullYear()} FleetTrack Management System. All rights reserved.</footer>
    </main>
  );
}

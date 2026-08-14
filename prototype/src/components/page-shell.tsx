import type { ReactNode } from "react";
import { SiteHeader } from "./site-header";
import { SiteFooter } from "./site-footer";

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main>{children}</main>
      <SiteFooter />
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  children?: ReactNode;
}) {
  return (
    <section className="relative overflow-hidden border-b border-border bg-secondary/50">
      <div className="pointer-events-none absolute inset-0 pattern-geo opacity-20" />
      <div className="relative mx-auto max-w-7xl px-5 py-14">
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">{eyebrow}</p>
        )}
        <h1 className="mt-3 max-w-3xl text-balance-tight font-display text-4xl leading-tight md:text-5xl">
          {title}
        </h1>
        {description && (
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
        {children}
      </div>
    </section>
  );
}

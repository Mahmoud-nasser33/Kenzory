import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowRight, Compass, MapPin, ShieldCheck, Users, Search } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { PlaceCard } from "@/components/place-card";
import { EgyptMap } from "@/components/egypt-map";
import { Button } from "@/components/ui/button";
import { places, stories, suggestedSearches, governorates } from "@/lib/kenzory-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Kenzory — Discover the Egypt You Never Knew" },
      {
        name: "description",
        content:
          "Explore forgotten places, hidden landmarks, and cultural heritage across Egypt, documented and verified by the people who know them.",
      },
      { property: "og:title", content: "Kenzory — Discover the Egypt You Never Knew" },
      {
        property: "og:description",
        content:
          "A community heritage platform mapping Egypt's lesser-known historical places, stories, and traditions.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  const [selected, setSelected] = useState<string | null>(places[0]!.id);

  return (
    <PageShell>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border bg-primary">
        <div className="pointer-events-none absolute inset-0 pattern-geo opacity-40" />
        <div className="pointer-events-none absolute -right-24 -top-24 size-[420px] rounded-full bg-accent/25 blur-3xl" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 py-16 lg:grid-cols-[1.05fr_1fr] lg:py-24">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-primary-foreground/15 bg-primary-foreground/10 px-3.5 py-1.5 text-xs font-medium text-primary-foreground/80">
              <Compass className="size-3.5 text-accent" />
              A community digital heritage initiative
            </span>
            <h1 className="mt-6 text-balance-tight font-display text-5xl leading-[1.02] text-primary-foreground md:text-7xl">
              The Egypt your <span className="italic text-accent">map forgot.</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-primary-foreground/75">
              Forgotten places, hidden landmarks, and local stories — found and documented by the
              people who actually know them.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button
                asChild
                size="lg"
                className="rounded-full bg-accent px-6 text-accent-foreground hover:bg-accent/90"
              >
                <Link to="/explore">
                  Explore Hidden Places <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="rounded-full border-primary-foreground/25 bg-transparent px-6 text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
              >
                <Link to="/add-place">Share a Discovery</Link>
              </Button>
            </div>

            <div className="mt-10 flex flex-wrap items-center gap-x-10 gap-y-4">
              <Stat value="1,284" label="Documented places" />
              <Stat value="27" label="Governorates covered" />
              <Stat value="4,910" label="Community photos" />
            </div>
          </div>

          <div className="relative">
            <div className="pointer-events-none absolute -inset-4 rounded-[999px_999px_1.5rem_1.5rem] bg-accent/20 blur-2xl" />
            <div className="arch-mask relative overflow-hidden border-4 border-primary-foreground/10 shadow-[var(--shadow-glow)]">
              <EgyptMap
                places={places}
                selectedId={selected}
                onSelect={setSelected}
                className="aspect-[4/5] w-full lg:aspect-square"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Search prompts */}
      <section className="border-b border-border bg-secondary/50">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-5 py-6">
          <span className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Search className="size-4 text-accent" /> Try searching
          </span>
          {suggestedSearches.map((s) => (
            <Link
              key={s}
              to="/explore"
              className="rounded-full border border-border bg-card px-3.5 py-1.5 text-sm text-muted-foreground shadow-[var(--shadow-soft)] transition-colors hover:border-accent/50 hover:text-foreground"
            >
              {s}
            </Link>
          ))}
        </div>
      </section>

      {/* Hidden around you */}
      <section className="mx-auto max-w-7xl px-5 py-20">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
              Hidden Around You
            </p>
            <h2 className="mt-3 font-display text-4xl">Places most maps have never listed</h2>
            <p className="mt-3 max-w-xl text-muted-foreground">
              You have 8 heritage sites within 30 km. Here are a few worth the drive.
            </p>
          </div>
          <Link
            to="/explore"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
          >
            View all discoveries <ArrowRight className="size-4" />
          </Link>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {places.slice(0, 6).map((p) => (
            <PlaceCard key={p.id} place={p} />
          ))}
        </div>
      </section>

      {/* Verification */}
      <section className="border-y border-border bg-secondary/50">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-20 lg:grid-cols-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
              Accuracy first
            </p>
            <h2 className="mt-3 font-display text-4xl">
              Every claim carries its <span className="italic">evidence</span> with it.
            </h2>
            <p className="mt-4 leading-relaxed text-muted-foreground">
              Kenzory never presents unverified claims as established history. Each place shows its
              verification state and the sources behind it.
            </p>
            <Link
              to="/about"
              className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
            >
              How verification works <ArrowRight className="size-4" />
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:col-span-2">
            <Pillar
              icon={<ShieldCheck className="size-5" />}
              title="Officially Verified"
              text="Cross-checked against Ministry of Tourism and Antiquities records or archaeological documentation."
            />
            <Pillar
              icon={<Users className="size-5" />}
              title="Community Verified"
              text="Confirmed on the ground by multiple trusted contributors with photographic evidence."
            />
            <Pillar
              icon={<Compass className="size-5" />}
              title="Under Review"
              text="Submitted and awaiting source checks. Displayed, but never stated as fact."
            />
            <Pillar
              icon={<MapPin className="size-5" />}
              title="Local Story"
              text="Oral history and memory, kept visibly separate from documented history."
            />
          </div>
        </div>
      </section>

      {/* Governorates */}
      <section className="mx-auto max-w-7xl px-5 py-20">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
          Explore by Governorate
        </p>
        <h2 className="mt-3 font-display text-4xl">All 27 governorates, one heritage map</h2>
        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {governorates.map((g, i) => (
            <Link
              key={g}
              to="/explore"
              className="surface-card group flex items-center justify-between rounded-xl px-4 py-3.5 transition-colors hover:border-accent/40"
            >
              <span className="text-sm font-medium">{g}</span>
              <span className="text-xs text-muted-foreground">{12 + ((i * 7) % 63)}</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Stories */}
      <section className="border-t border-border bg-secondary/40">
        <div className="mx-auto max-w-7xl px-5 py-20">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
                Stories
              </p>
              <h2 className="mt-3 font-display text-4xl">The human side of heritage</h2>
            </div>
            <Link
              to="/stories"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
            >
              Read all stories <ArrowRight className="size-4" />
            </Link>
          </div>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {stories.map((s) => (
              <Link
                key={s.id}
                to="/stories"
                className="group surface-card overflow-hidden rounded-2xl transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-lift)]"
              >
                <img
                  src={s.image}
                  alt={s.title}
                  loading="lazy"
                  width={1200}
                  height={800}
                  className="aspect-[16/10] w-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="p-6">
                  <p className="text-xs uppercase tracking-widest text-muted-foreground">
                    {s.place} · {s.readMinutes} min read
                  </p>
                  <h3 className="mt-2 font-display text-2xl leading-snug">{s.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{s.excerpt}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-5 py-20">
        <div className="relative overflow-hidden rounded-3xl bg-primary px-8 py-16 text-center text-primary-foreground md:px-16">
          <div className="pointer-events-none absolute inset-0 pattern-geo opacity-25" />
          <div className="pointer-events-none absolute left-1/2 top-0 h-px w-2/3 -translate-x-1/2 bg-gradient-to-r from-transparent via-accent/60 to-transparent" />
          <div className="relative">
            <h2 className="mx-auto max-w-2xl text-balance-tight font-display text-4xl leading-tight md:text-5xl">
              Help preserve a piece of <span className="italic text-accent">Egypt's history.</span>
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-primary-foreground/75">
              If you know a place that deserves to be remembered, document it. One record can keep a
              building, a craft, or a story from disappearing.
            </p>
            <Button
              asChild
              size="lg"
              className="mt-8 rounded-full bg-accent px-7 text-accent-foreground hover:bg-accent/90"
            >
              <Link to="/add-place">
                Share a Discovery <ArrowRight className="size-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </PageShell>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <p className="font-display text-3xl text-primary-foreground">{value}</p>
      <p className="text-xs uppercase tracking-widest text-primary-foreground/60">{label}</p>
    </div>
  );
}

function Pillar({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="surface-card group rounded-2xl p-6 transition-colors hover:border-accent/40">
      <span className="flex size-10 items-center justify-center rounded-full border border-accent/25 text-accent transition-colors group-hover:bg-accent group-hover:text-accent-foreground">
        {icon}
      </span>
      <h3 className="mt-4 font-display text-xl">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{text}</p>
    </div>
  );
}

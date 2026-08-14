import { createFileRoute } from "@tanstack/react-router";
import { PageShell } from "@/components/page-shell";
import { PlaceCard } from "@/components/place-card";
import { places, profile } from "@/lib/kenzory-data";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: `${profile.name} — Contributor Profile | Kenzory` },
      {
        name: "description",
        content:
          "Contributor profile showing documented heritage discoveries, verified records, photos, and reputation on Kenzory.",
      },
      { property: "og:title", content: `${profile.name} — Kenzory Contributor` },
      {
        property: "og:description",
        content: "Discoveries, verified records, and photos contributed to Egypt's heritage archive.",
      },
    ],
  }),
  component: Profile,
});

function Profile() {
  return (
    <PageShell>
      <section className="border-b border-border bg-secondary/40">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-8 px-5 py-14">
          <span className="flex size-24 items-center justify-center rounded-2xl bg-accent text-4xl font-semibold text-accent-foreground">
            {profile.initials}
          </span>
          <div className="min-w-64 flex-1">
            <h1 className="font-display text-4xl">{profile.name}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {profile.handle} · <span className="text-accent">{profile.level}</span>
            </p>
            <p className="mt-4 max-w-xl leading-relaxed text-muted-foreground">{profile.bio}</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {profile.badges.map((b) => (
                <span
                  key={b}
                  className="rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground"
                >
                  {b}
                </span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Stat value={`${profile.discoveries}`} label="Discoveries" />
            <Stat value={`${profile.verified}`} label="Verified" />
            <Stat value={`${profile.photos}`} label="Photos" />
            <Stat value={`${profile.saved}`} label="Saved places" />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-12">
        <div className="surface-card rounded-2xl p-7">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="font-display text-2xl">Contributor reputation</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Weighted by source quality, verification outcomes, and photo usefulness — not
                submission count.
              </p>
            </div>
            <p className="font-display text-4xl text-accent">{profile.reputation}/100</p>
          </div>
          <div className="mt-6 h-2.5 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full rounded-full bg-accent"
              style={{ width: `${profile.reputation}%` }}
            />
          </div>
          <div className="mt-6 grid gap-5 sm:grid-cols-3">
            <Meter label="Source quality" value={82} />
            <Meter label="Verification rate" value={65} />
            <Meter label="Photo documentation" value={78} />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-16">
        <h2 className="font-display text-3xl">Discoveries by {profile.name}</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {places.slice(0, 3).map((p) => (
            <PlaceCard key={p.id} place={p} />
          ))}
        </div>

        <h2 className="mt-16 font-display text-3xl">Saved places</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {places.slice(3).map((p) => (
            <PlaceCard key={p.id} place={p} />
          ))}
        </div>
        <p className="mt-10 text-xs text-muted-foreground">Demo profile with sample data.</p>
      </section>
    </PageShell>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="surface-card rounded-xl px-5 py-4 text-center">
      <p className="font-display text-3xl">{value}</p>
      <p className="mt-1 text-[11px] uppercase tracking-widest text-muted-foreground">{label}</p>
    </div>
  );
}

function Meter({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-secondary">
        <div className="h-full rounded-full bg-primary" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useState } from "react";
import {
  MapPin,
  Bookmark,
  Share2,
  Flag,
  Calendar,
  Layers,
  BookOpen,
  ArrowRight,
} from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { PlaceCard } from "@/components/place-card";
import { EgyptMap } from "@/components/egypt-map";
import { VerificationBadge, LocalStoryBadge } from "@/components/verification-badge";
import { Button } from "@/components/ui/button";
import { getPlace, places } from "@/lib/kenzory-data";

export const Route = createFileRoute("/place/$placeId")({
  loader: ({ params }) => {
    const place = getPlace(params.placeId);
    if (!place) throw notFound();
    return place;
  },
  head: ({ loaderData }) => ({
    meta: loaderData
      ? [
          { title: `${loaderData.name}, ${loaderData.governorate} | Kenzory` },
          { name: "description", content: loaderData.summary },
          { property: "og:title", content: `${loaderData.name} — ${loaderData.governorate}` },
          { property: "og:description", content: loaderData.summary },
        ]
      : [],
  }),
  component: PlaceDetail,
});

function PlaceDetail() {
  const place = Route.useLoaderData();
  const [active, setActive] = useState(0);
  const nearby = places.filter((p) => p.id !== place.id).slice(0, 3);

  return (
    <PageShell>
      {/* Gallery */}
      <section className="mx-auto max-w-7xl px-5 pt-8">
        <div className="grid gap-3 lg:grid-cols-[2fr_1fr]">
          <img
            src={place.gallery[active] ?? place.image}
            alt={place.name}
            width={1200}
            height={800}
            className="aspect-[16/10] w-full rounded-2xl object-cover lg:aspect-auto lg:h-[34rem]"
          />
          <div className="grid grid-cols-3 gap-3 lg:h-[34rem] lg:grid-cols-1 lg:grid-rows-3">
            {place.gallery.map((g, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={
                  "overflow-hidden rounded-xl border-2 transition-colors lg:h-full " +
                  (i === active ? "border-accent" : "border-transparent hover:border-border")
                }
              >
                <img
                  src={g}
                  alt={`${place.name} photo ${i + 1}`}
                  loading="lazy"
                  width={1200}
                  height={800}
                  className="aspect-[4/3] w-full object-cover lg:aspect-auto lg:h-full"
                />
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Header */}
      <section className="mx-auto max-w-7xl px-5 py-10">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <VerificationBadge status={place.verification} />
              <span className="rounded-full bg-secondary px-2.5 py-1 text-[11px] font-medium text-secondary-foreground">
                {place.category}
              </span>
            </div>
            <h1 className="mt-4 font-display text-5xl leading-tight">{place.name}</h1>
            <p className="mt-2 font-arabic text-2xl text-muted-foreground" dir="rtl">
              {place.nameAr}
            </p>
            <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <MapPin className="size-4" />
                {place.city}, {place.governorate}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Calendar className="size-4" />
                {place.period} · {place.approxDate}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Layers className="size-4" />
                {place.photos} photos · {place.saves} saves
              </span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button className="rounded-full">
              <Bookmark className="size-4" /> Save
            </Button>
            <Button variant="outline" className="rounded-full">
              <Share2 className="size-4" /> Share
            </Button>
            <Button variant="ghost" className="rounded-full">
              <Flag className="size-4" /> Report
            </Button>
          </div>
        </div>
      </section>

      <div className="mx-auto grid max-w-7xl gap-12 px-5 pb-16 lg:grid-cols-[1fr_21rem]">
        <div className="space-y-12">
          <Block title="Historical description">
            <p className="leading-relaxed text-muted-foreground">{place.description}</p>
          </Block>

          <Block title="Why it matters">
            <p className="leading-relaxed text-muted-foreground">{place.whyItMatters}</p>
          </Block>

          <Block title="Architecture and features">
            <ul className="grid gap-3 sm:grid-cols-2">
              {place.architecture.map((a) => (
                <li
                  key={a}
                  className="rounded-xl border border-border bg-card px-4 py-3 text-sm text-muted-foreground"
                >
                  {a}
                </li>
              ))}
            </ul>
          </Block>

          <Block title="Historical timeline">
            <ol className="relative space-y-6 border-l border-border pl-6">
              {place.timeline.map((t) => (
                <li key={t.year} className="relative">
                  <span className="absolute -left-[1.68rem] top-1.5 size-2.5 rounded-full bg-accent" />
                  <p className="font-display text-xl">{t.year}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{t.event}</p>
                </li>
              ))}
            </ol>
          </Block>

          <Block title="Local stories">
            <p className="mb-4 text-sm text-muted-foreground">
              Community memory, kept separate from documented history.
            </p>
            <div className="space-y-4">
              {place.stories.map((s) => (
                <div key={s.title} className="rounded-2xl border border-accent/25 bg-accent/5 p-6">
                  <LocalStoryBadge />
                  <h3 className="mt-3 font-display text-xl">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.text}</p>
                  <p className="mt-3 text-xs text-muted-foreground">Told by {s.author}</p>
                </div>
              ))}
            </div>
          </Block>

          <Block title="Location">
            <EgyptMap
              places={[place]}
              selectedId={place.id}
              className="aspect-[16/9]"
              showControls={false}
            />
          </Block>

          <Block title="Sources and references">
            <ul className="space-y-3">
              {place.sources.map((s) => (
                <li
                  key={s.label}
                  className="flex items-start gap-3 rounded-xl border border-border bg-card p-4"
                >
                  <BookOpen className="mt-0.5 size-4 shrink-0 text-accent" />
                  <div>
                    <p className="text-sm font-medium">{s.label}</p>
                    <p className="text-xs text-muted-foreground">{s.type}</p>
                  </div>
                </li>
              ))}
            </ul>
          </Block>
        </div>

        <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
          <div className="surface-card rounded-2xl p-6">
            <h3 className="font-display text-xl">Verification</h3>
            <div className="mt-3">
              <VerificationBadge status={place.verification} />
            </div>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              {place.verification === "official"
                ? "Matched against official records and academic sources."
                : place.verification === "community"
                  ? "Confirmed on the ground by trusted contributors with dated photos."
                  : place.verification === "review"
                    ? "Reported but not confirmed. Treat details as provisional."
                    : "No documentary source located yet. Recorded so the place is not lost."}
            </p>
            <Link
              to="/about"
              className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
            >
              Verification standards <ArrowRight className="size-3.5" />
            </Link>
          </div>

          <div className="surface-card rounded-2xl p-6">
            <h3 className="font-display text-xl">Contributor</h3>
            <Link to="/profile" className="mt-4 flex items-center gap-3">
              <span className="flex size-11 items-center justify-center rounded-full bg-accent/15 font-semibold text-accent">
                {place.contributor.initials}
              </span>
              <div>
                <p className="font-medium">{place.contributor.name}</p>
                <p className="text-xs text-muted-foreground">{place.contributor.level}</p>
              </div>
            </Link>
            <p className="mt-4 text-xs text-muted-foreground">Added {place.addedAgo}</p>
          </div>

          <div className="rounded-2xl border border-border bg-secondary/50 p-6">
            <h3 className="font-display text-lg">Plan a visit</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {place.distanceKm} km away · ~{place.visitMinutes} minutes on site
            </p>
            <Button asChild variant="outline" className="mt-4 w-full rounded-full">
              <Link to="/map">Open on map</Link>
            </Button>
          </div>
        </aside>
      </div>

      <section className="mx-auto max-w-7xl px-5 pb-20">
        <h2 className="font-display text-3xl">Nearby historical places</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {nearby.map((p) => (
            <PlaceCard key={p.id} place={p} />
          ))}
        </div>
      </section>
    </PageShell>
  );
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-4 font-display text-3xl">{title}</h2>
      {children}
    </section>
  );
}

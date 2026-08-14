import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { PageShell, PageHeader } from "@/components/page-shell";
import { PlaceCard } from "@/components/place-card";
import { Input } from "@/components/ui/input";
import {
  categories,
  governorates,
  periods,
  places,
  suggestedSearches,
} from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/explore")({
  head: () => ({
    meta: [
      { title: "Explore Hidden Heritage Places in Egypt | Kenzory" },
      {
        name: "description",
        content:
          "Search and filter lesser-known Egyptian heritage sites by category, historical period, and governorate.",
      },
      { property: "og:title", content: "Explore Hidden Heritage Places in Egypt" },
      {
        property: "og:description",
        content: "Filter Egypt's documented hidden heritage by category, period, and governorate.",
      },
    ],
  }),
  component: Explore,
});

function Explore() {
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<string>("All");
  const [period, setPeriod] = useState<string>("All");
  const [gov, setGov] = useState<string>("All");

  const results = useMemo(
    () =>
      places.filter((p) => {
        const q = query.trim().toLowerCase();
        const matchQ =
          !q ||
          [p.name, p.nameAr, p.governorate, p.city, p.category, p.period, p.contributor.name]
            .join(" ")
            .toLowerCase()
            .includes(q);
        return (
          matchQ &&
          (cat === "All" || p.category === cat) &&
          (period === "All" || p.period === period) &&
          (gov === "All" || p.governorate === gov)
        );
      }),
    [query, cat, period, gov],
  );

  return (
    <PageShell>
      <PageHeader
        eyebrow="Explore"
        title="Search Egypt's lesser-known heritage"
        description="Every record shows where its information comes from. Filter by what interests you — or by what's near you."
      >
        <div className="mt-8 flex max-w-2xl items-center gap-3 rounded-full border border-border bg-card px-5 py-2 shadow-[var(--shadow-soft)]">
          <Search className="size-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Place, governorate, city, category, period, or contributor…"
            className="border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
          />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {suggestedSearches.map((s) => (
            <button
              key={s}
              onClick={() => setQuery(s.replace(/^(Hidden|Historic|Unknown) /, "").split(" in ")[0] ?? s)}
              className="rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
            >
              {s}
            </button>
          ))}
        </div>
      </PageHeader>

      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-12 lg:grid-cols-[16rem_1fr]">
        <aside className="space-y-8">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <SlidersHorizontal className="size-4 text-accent" /> Filters
          </div>
          <FilterGroup
            title="Category"
            options={["All", ...categories]}
            value={cat}
            onChange={setCat}
          />
          <FilterGroup
            title="Historical period"
            options={["All", ...periods]}
            value={period}
            onChange={setPeriod}
          />
          <FilterGroup
            title="Governorate"
            options={["All", ...governorates.slice(0, 12)]}
            value={gov}
            onChange={setGov}
          />
        </aside>

        <div>
          <p className="mb-6 text-sm text-muted-foreground">
            {results.length} place{results.length === 1 ? "" : "s"} found · demo dataset
          </p>
          {results.length ? (
            <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
              {results.map((p) => (
                <PlaceCard key={p.id} place={p} />
              ))}
            </div>
          ) : (
            <div className="surface-card rounded-2xl p-12 text-center">
              <h3 className="font-display text-2xl">Nothing documented here yet</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                That's exactly the gap Kenzory exists to close. Try another filter, or add the place
                yourself.
              </p>
            </div>
          )}
        </div>
      </div>
    </PageShell>
  );
}

function FilterGroup({
  title,
  options,
  value,
  onChange,
}: {
  title: string;
  options: readonly string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        {title}
      </h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {options.map((o) => (
          <button
            key={o}
            onClick={() => onChange(o)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs transition-colors",
              value === o
                ? "border-accent bg-accent text-accent-foreground"
                : "border-border bg-card text-muted-foreground hover:text-foreground",
            )}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  );
}

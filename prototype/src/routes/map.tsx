import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, LocateFixed } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { EgyptMap } from "@/components/egypt-map";
import { VerificationBadge } from "@/components/verification-badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { categories, governorates, periods, places } from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/map")({
  head: () => ({
    meta: [
      { title: "Interactive Heritage Map of Egypt | Kenzory" },
      {
        name: "description",
        content:
          "Pan and zoom an interactive map of Egypt to find hidden heritage sites near you, filtered by category, period, and governorate.",
      },
      { property: "og:title", content: "Interactive Heritage Map of Egypt" },
      {
        property: "og:description",
        content: "Find documented hidden heritage sites across Egypt on an interactive map.",
      },
    ],
  }),
  component: MapPage,
});

function MapPage() {
  const [selected, setSelected] = useState<string | null>(places[0]!.id);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState("All");
  const [period, setPeriod] = useState("All");
  const [gov, setGov] = useState("All");
  const [nearby, setNearby] = useState(false);

  const filtered = useMemo(
    () =>
      places.filter((p) => {
        const q = query.trim().toLowerCase();
        return (
          (!q || `${p.name} ${p.nameAr} ${p.city} ${p.governorate}`.toLowerCase().includes(q)) &&
          (cat === "All" || p.category === cat) &&
          (period === "All" || p.period === period) &&
          (gov === "All" || p.governorate === gov) &&
          (!nearby || p.distanceKm <= 30)
        );
      }),
    [query, cat, period, gov, nearby],
  );

  return (
    <PageShell>
      <div className="mx-auto grid max-w-[100rem] gap-6 px-5 py-8 lg:grid-cols-[22rem_1fr]">
        <aside className="space-y-6">
          <div>
            <h1 className="font-display text-3xl">Map of hidden Egypt</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {filtered.length} sites shown · live map of Egypt
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5">
            <Search className="size-4 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search locations"
              className="border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
            />
          </div>

          <Button
            variant={nearby ? "default" : "outline"}
            className="w-full rounded-full"
            onClick={() => setNearby((v) => !v)}
          >
            <LocateFixed className="size-4" />
            Places near me (30 km)
          </Button>

          <Select label="Category" options={["All", ...categories]} value={cat} onChange={setCat} />
          <Select
            label="Historical period"
            options={["All", ...periods]}
            value={period}
            onChange={setPeriod}
          />
          <Select
            label="Governorate"
            options={["All", ...governorates.slice(0, 12)]}
            value={gov}
            onChange={setGov}
          />

          <div className="space-y-3 border-t border-border pt-5">
            {filtered.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelected(p.id)}
                className={cn(
                  "flex w-full gap-3 rounded-xl border p-3 text-left transition-colors",
                  selected === p.id
                    ? "border-accent bg-accent/5"
                    : "border-border bg-card hover:border-accent/40",
                )}
              >
                <img
                  src={p.image}
                  alt={p.name}
                  loading="lazy"
                  width={1200}
                  height={800}
                  className="size-16 shrink-0 rounded-lg object-cover"
                />
                <div className="min-w-0">
                  <p className="truncate font-medium">{p.name}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {p.city}, {p.governorate}
                  </p>
                  <div className="mt-1.5">
                    <VerificationBadge status={p.verification} />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </aside>

        <EgyptMap
          places={filtered}
          selectedId={selected}
          onSelect={setSelected}
          className="min-h-[36rem] lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]"
        />
      </div>
    </PageShell>
  );
}

function Select({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: readonly string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-2 w-full rounded-lg border border-border bg-card px-3 py-2.5 text-sm outline-none focus:border-accent"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Heart, Bookmark, MessageCircle, Share2, Flag, ArrowRight } from "lucide-react";
import { PageShell, PageHeader } from "@/components/page-shell";
import { VerificationBadge } from "@/components/verification-badge";
import { feed, places } from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/discoveries")({
  head: () => ({
    meta: [
      { title: "Community Discoveries Feed | Kenzory" },
      {
        name: "description",
        content:
          "See newly documented Egyptian heritage places, verification updates, and photo sets added by the Kenzory community.",
      },
      { property: "og:title", content: "Community Discoveries Feed" },
      {
        property: "og:description",
        content: "Recently added Egyptian heritage places and verification updates.",
      },
    ],
  }),
  component: Discoveries,
});

function Discoveries() {
  return (
    <PageShell>
      <PageHeader
        eyebrow="Discoveries"
        title="What the community found this week"
        description="New records, verification changes, and fresh photography from across Egypt."
      />

      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-6">
          {feed.map((item) => (
            <FeedCard key={item.id} item={item} />
          ))}
        </div>

        <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
          <div className="surface-card rounded-2xl p-6">
            <h3 className="font-display text-xl">Hidden Gems Near You</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              You have 8 heritage sites within 30 km.
            </p>
            <div className="mt-5 space-y-4">
              {places.slice(0, 3).map((p) => (
                <Link
                  key={p.id}
                  to="/place/$placeId"
                  params={{ placeId: p.id }}
                  className="flex gap-3 rounded-xl p-2 transition-colors hover:bg-secondary"
                >
                  <img
                    src={p.image}
                    alt={p.name}
                    loading="lazy"
                    width={1200}
                    height={800}
                    className="size-14 shrink-0 rounded-lg object-cover"
                  />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{p.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {p.distanceKm} km · ~{p.visitMinutes} min · {p.period}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
            <Link
              to="/map"
              className="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
            >
              Open the map <ArrowRight className="size-4" />
            </Link>
          </div>

          <div className="surface-card rounded-2xl p-6">
            <h3 className="font-display text-xl">Top contributors</h3>
            <ul className="mt-4 space-y-4">
              {[
                { n: "Mariam", l: "Senior Documenter", d: 34 },
                { n: "Mahmoud", l: "Heritage Explorer", d: 17 },
                { n: "Ahmed", l: "Field Documenter", d: 12 },
              ].map((c) => (
                <li key={c.n} className="flex items-center gap-3">
                  <span className="flex size-9 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent">
                    {c.n[0]}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{c.n}</p>
                    <p className="text-xs text-muted-foreground">
                      {c.l} · {c.d} discoveries
                    </p>
                  </div>
                </li>
              ))}
            </ul>
            <Link
              to="/profile"
              className="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline"
            >
              View a profile <ArrowRight className="size-4" />
            </Link>
          </div>
        </aside>
      </div>
    </PageShell>
  );
}

function FeedCard({ item }: { item: (typeof feed)[number] }) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);

  return (
    <article className="surface-card overflow-hidden rounded-2xl">
      <div className="grid sm:grid-cols-[14rem_1fr]">
        <img
          src={item.image}
          alt={item.title}
          loading="lazy"
          width={1200}
          height={800}
          className="h-full min-h-40 w-full object-cover"
        />
        <div className="p-6">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-primary">
              {item.kind}
            </span>
            <VerificationBadge status={item.verification} />
          </div>
          <h2 className="mt-3 font-display text-2xl leading-snug">{item.title}</h2>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
          <p className="mt-3 text-xs text-muted-foreground">
            Added by {item.author} · {item.ago}
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-1 border-t border-border pt-4">
            <Action
              icon={<Heart className={cn("size-4", liked && "fill-accent text-accent")} />}
              label={`${item.likes + (liked ? 1 : 0)}`}
              onClick={() => setLiked((v) => !v)}
            />
            <Action icon={<MessageCircle className="size-4" />} label={`${item.comments}`} />
            <Action
              icon={<Bookmark className={cn("size-4", saved && "fill-accent text-accent")} />}
              label={saved ? "Saved" : "Save"}
              onClick={() => setSaved((v) => !v)}
            />
            <Action icon={<Share2 className="size-4" />} label="Share" />
            <Action icon={<Flag className="size-4" />} label="Report" className="ml-auto" />
          </div>
        </div>
      </div>
    </article>
  );
}

function Action({
  icon,
  label,
  onClick,
  className,
}: {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground",
        className,
      )}
    >
      {icon}
      {label}
    </button>
  );
}

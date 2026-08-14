import { createFileRoute } from "@tanstack/react-router";
import { PageShell, PageHeader } from "@/components/page-shell";
import { stories, images } from "@/lib/kenzory-data";

export const Route = createFileRoute("/stories")({
  head: () => ({
    meta: [
      { title: "Heritage Stories from Across Egypt | Kenzory" },
      {
        name: "description",
        content:
          "Long-form stories about forgotten mosques, abandoned stations, and vanishing crafts, told by the communities who live beside them.",
      },
      { property: "og:title", content: "Heritage Stories from Across Egypt" },
      {
        property: "og:description",
        content: "Editorial stories about the human side of Egypt's lesser-known heritage.",
      },
    ],
  }),
  component: Stories,
});

function Stories() {
  const [lead, ...rest] = stories as [(typeof stories)[number], ...(typeof stories)[number][]];

  return (
    <PageShell>
      <PageHeader
        eyebrow="Stories"
        title="Heritage is people, not only stone."
        description="Reported and edited pieces about the places in our archive — and the communities keeping them alive."
      />

      <div className="mx-auto max-w-7xl px-5 py-14">
        <article className="group grid gap-8 overflow-hidden rounded-3xl border border-border bg-card shadow-[var(--shadow-soft)] lg:grid-cols-2">
          <img
            src={lead.image}
            alt={lead.title}
            width={1200}
            height={800}
            className="h-full min-h-[22rem] w-full object-cover"
          />
          <div className="flex flex-col justify-center p-8 lg:p-12">
            <p className="text-xs uppercase tracking-[0.22em] text-accent">Featured story</p>
            <h2 className="mt-4 font-display text-4xl leading-tight">{lead.title}</h2>
            <p className="mt-4 leading-relaxed text-muted-foreground">{lead.excerpt}</p>
            <p className="mt-6 text-sm text-muted-foreground">
              By {lead.author} · {lead.place} · {lead.readMinutes} min read
            </p>
          </div>
        </article>

        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {rest.map((s) => (
            <article
              key={s.id}
              className="group surface-card overflow-hidden rounded-2xl transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-lift)]"
            >
              <img
                src={s.image}
                alt={s.title}
                loading="lazy"
                width={1200}
                height={800}
                className="aspect-[16/9] w-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="p-7">
                <p className="text-xs uppercase tracking-widest text-muted-foreground">
                  {s.place} · {s.readMinutes} min read
                </p>
                <h3 className="mt-2 font-display text-2xl leading-snug">{s.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{s.excerpt}</p>
                <p className="mt-5 text-sm text-muted-foreground">By {s.author}</p>
              </div>
            </article>
          ))}
          <article className="surface-card flex flex-col justify-center rounded-2xl p-8">
            <img
              src={images.temple}
              alt="Desert temple terrace"
              loading="lazy"
              width={1200}
              height={800}
              className="mb-6 aspect-[16/9] w-full rounded-xl object-cover"
            />
            <h3 className="font-display text-2xl">Write for Kenzory</h3>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              If you grew up beside a place nobody writes about, you already know the story worth
              telling. We edit alongside contributors and always credit local voices.
            </p>
          </article>
        </div>

        <p className="mt-10 text-xs text-muted-foreground">
          Demo content — stories shown here are illustrative prototype material.
        </p>
      </div>
    </PageShell>
  );
}

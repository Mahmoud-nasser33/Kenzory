import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { PageShell, PageHeader } from "@/components/page-shell";
import { VerificationBadge } from "@/components/verification-badge";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About Kenzory — Documenting Egypt's Hidden Heritage" },
      {
        name: "description",
        content:
          "Kenzory is a community initiative to discover, document, and preserve Egypt's lesser-known historical and cultural heritage with verifiable sources.",
      },
      { property: "og:title", content: "About Kenzory" },
      {
        property: "og:description",
        content:
          "How Kenzory documents and verifies Egypt's lesser-known historical and cultural heritage.",
      },
    ],
  }),
  component: About,
});

const levels = [
  {
    status: "official" as const,
    text: "Cross-checked against Ministry of Tourism and Antiquities records, archaeological reports, or peer-reviewed publications.",
  },
  {
    status: "community" as const,
    text: "Independently confirmed on site by multiple trusted contributors, with dated photographic evidence.",
  },
  {
    status: "review" as const,
    text: "Submitted with partial evidence. Visible to the community, explicitly marked as provisional.",
  },
  {
    status: "unverified" as const,
    text: "No documentary source located yet. Recorded so the place is not lost, never presented as established fact.",
  },
];

function About() {
  return (
    <PageShell>
      <PageHeader
        eyebrow="About"
        title="Egypt has thousands of stories hiding in plain sight."
        description="Kenzory helps people find them, document them, and make sure they are not forgotten — through open community contribution and strict sourcing."
      />

      <section className="mx-auto grid max-w-7xl gap-12 px-5 py-16 lg:grid-cols-2">
        <div className="space-y-5 text-lg leading-relaxed text-muted-foreground">
          <p>
            Most of Egypt's heritage is not on a tour route. It is a provincial mosque, a closed
            railway hall, a mudbrick house with painted bands, a craft workshop with three people
            left in it. These places are rarely surveyed and almost never photographed before they
            change.
          </p>
          <p>
            Kenzory is built for the people closest to them: residents, students, photographers,
            researchers, and travellers who go where guidebooks do not. Contributors add places,
            evidence, and oral history; the platform keeps documented history and community memory
            clearly apart.
          </p>
        </div>
        <div className="surface-card rounded-2xl p-8">
          <h2 className="font-display text-2xl">Our commitments</h2>
          <ul className="mt-5 space-y-4 text-sm leading-relaxed text-muted-foreground">
            <li>
              <strong className="text-foreground">Accuracy over volume.</strong> Reputation is
              earned through sourced, verifiable contributions — not submission counts.
            </li>
            <li>
              <strong className="text-foreground">Local credit.</strong> The person who documented a
              place is named on it, permanently.
            </li>
            <li>
              <strong className="text-foreground">Sensitive locations.</strong> Coordinates for
              at-risk sites can be generalised on request to reduce looting risk.
            </li>
            <li>
              <strong className="text-foreground">Bilingual by default.</strong> Every record
              supports Arabic and English naming and description.
            </li>
          </ul>
        </div>
      </section>

      <section className="border-y border-border bg-secondary/40">
        <div className="mx-auto max-w-7xl px-5 py-16">
          <h2 className="font-display text-4xl">Verification standards</h2>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Accepted source types include Ministry of Tourism and Antiquities records, archaeological
            records, academic publications, books, historical archives, and dated local
            documentation.
          </p>
          <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {levels.map((l) => (
              <div key={l.status} className="surface-card rounded-2xl p-6">
                <VerificationBadge status={l.status} />
                <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{l.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16">
        <div className="surface-card flex flex-wrap items-center justify-between gap-6 rounded-3xl p-10">
          <div>
            <h2 className="font-display text-3xl">Know a place worth keeping?</h2>
            <p className="mt-2 text-muted-foreground">
              Help preserve a piece of Egypt's history.
            </p>
          </div>
          <Button asChild size="lg" className="rounded-full px-7">
            <Link to="/add-place">
              Add a Place <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
        <p className="mt-8 text-xs text-muted-foreground">
          Prototype notice: Kenzory is shown here as a design prototype. All places, contributors,
          statistics, and stories are demo data.
        </p>
      </section>
    </PageShell>
  );
}

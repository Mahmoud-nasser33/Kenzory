import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { CheckCircle2, ImagePlus, MapPin, ShieldCheck, ArrowRight } from "lucide-react";
import { PageShell, PageHeader } from "@/components/page-shell";
import { EgyptMap } from "@/components/egypt-map";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { categories, governorates, periods, places } from "@/lib/kenzory-data";

export const Route = createFileRoute("/add-place")({
  head: () => ({
    meta: [
      { title: "Add a Heritage Place | Kenzory" },
      {
        name: "description",
        content:
          "Submit a lesser-known Egyptian heritage site with photos, history, local stories, and sources for community verification.",
      },
      { property: "og:title", content: "Add a Heritage Place to Kenzory" },
      {
        property: "og:description",
        content: "Help preserve a piece of Egypt's history by documenting a place you know.",
      },
    ],
  }),
  component: AddPlace,
});

function AddPlace() {
  const [submitted, setSubmitted] = useState(false);
  const [pin, setPin] = useState<string | null>(places[2]!.id);

  if (submitted) {
    return (
      <PageShell>
        <div className="mx-auto max-w-2xl px-5 py-28 text-center">
          <span className="mx-auto flex size-16 items-center justify-center rounded-full bg-primary/10 text-primary">
            <CheckCircle2 className="size-8" />
          </span>
          <h1 className="mt-8 font-display text-4xl">
            Your discovery has been submitted for review.
          </h1>
          <p className="mt-4 leading-relaxed text-muted-foreground">
            A reviewer will check your sources and photos. You'll see the record appear as{" "}
            <strong className="text-foreground">Under Review</strong> in the discoveries feed, and
            it moves to Community or Officially Verified once evidence is confirmed.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button asChild className="rounded-full px-6">
              <Link to="/discoveries">
                View the feed <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              variant="outline"
              className="rounded-full px-6"
              onClick={() => setSubmitted(false)}
            >
              Submit another place
            </Button>
          </div>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        eyebrow="Contribute"
        title="Help preserve a piece of Egypt's history."
        description="Document a place that is not yet recorded. Sources are optional to submit, but they determine how far the record can be verified."
      />

      <form
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(true);
        }}
        className="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[1fr_22rem]"
      >
        <div className="space-y-10">
          <Section title="Identity" step="01">
            <Field label="Place name (English)" required>
              <Input required placeholder="e.g. Historic Mosque of Al-Hamawi" />
            </Field>
            <Field label="Arabic name">
              <Input dir="rtl" className="font-arabic" placeholder="اسم المكان بالعربية" />
            </Field>
            <Field label="Governorate" required>
              <SelectInput options={governorates} />
            </Field>
            <Field label="Category" required>
              <SelectInput options={categories} />
            </Field>
            <Field label="Historical period">
              <SelectInput options={periods} />
            </Field>
            <Field label="Estimated date">
              <Input placeholder="e.g. c. 1710 CE, or 5th–6th century" />
            </Field>
          </Section>

          <Section title="Location" step="02">
            <div className="sm:col-span-2">
              <p className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="size-4 text-accent" /> Drop a pin on the map. You can generalise
                coordinates for at-risk sites.
              </p>
              <EgyptMap
                places={places}
                selectedId={pin}
                onSelect={setPin}
                className="aspect-[16/10]"
              />
            </div>
          </Section>

          <Section title="History and meaning" step="03">
            <Field label="Description" required className="sm:col-span-2">
              <Textarea
                required
                rows={5}
                placeholder="What is the place, what survives, and what is its history?"
              />
            </Field>
            <Field label="Why this place is important" className="sm:col-span-2">
              <Textarea rows={4} placeholder="Why does it deserve to be documented and preserved?" />
            </Field>
            <Field label="Local stories" className="sm:col-span-2">
              <Textarea
                rows={4}
                placeholder="Oral history, memories, local names. Marked separately from documented history."
              />
            </Field>
          </Section>

          <Section title="Evidence" step="04">
            <div className="sm:col-span-2">
              <Label className="text-sm">Photos</Label>
              <div className="mt-2 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-border bg-secondary/40 p-10 text-center">
                <ImagePlus className="size-6 text-accent" />
                <p className="mt-3 text-sm font-medium">Drag photos here or browse</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Dated, uncropped originals help verification most (demo upload)
                </p>
              </div>
            </div>
            <Field label="References / sources" className="sm:col-span-2">
              <Textarea
                rows={3}
                placeholder="Ministry records, archaeological reports, academic publications, books, archives, local documentation…"
              />
            </Field>
            <Field label="Additional notes" className="sm:col-span-2">
              <Textarea rows={3} placeholder="Access, condition, risks, best time to visit…" />
            </Field>
          </Section>

          <div className="flex flex-wrap items-center gap-4">
            <Button type="submit" size="lg" className="rounded-full px-8">
              Submit for review
            </Button>
            <p className="text-xs text-muted-foreground">
              Prototype form — nothing is stored or sent.
            </p>
          </div>
        </div>

        <aside className="space-y-5 lg:sticky lg:top-24 lg:self-start">
          <div className="surface-card rounded-2xl p-6">
            <span className="flex size-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <ShieldCheck className="size-5" />
            </span>
            <h3 className="mt-4 font-display text-xl">What happens next</h3>
            <ol className="mt-4 space-y-3 text-sm text-muted-foreground">
              <li>1. Submission enters the queue as Under Review.</li>
              <li>2. Reviewers check sources and photo evidence.</li>
              <li>3. A second contributor confirms on the ground.</li>
              <li>4. Record becomes Community or Officially Verified.</li>
            </ol>
          </div>
          <div className="rounded-2xl border border-accent/30 bg-accent/5 p-6">
            <h3 className="font-display text-lg">Please don't guess</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              If you're unsure about a date or attribution, say so in the notes. Uncertain records
              are still valuable — invented ones are not.
            </p>
          </div>
        </aside>
      </form>
    </PageShell>
  );
}

function Section({
  title,
  step,
  children,
}: {
  title: string;
  step: string;
  children: React.ReactNode;
}) {
  return (
    <section className="surface-card rounded-2xl p-7">
      <div className="flex items-center gap-3">
        <span className="font-display text-sm text-accent">{step}</span>
        <h2 className="font-display text-2xl">{title}</h2>
      </div>
      <div className="mt-6 grid gap-5 sm:grid-cols-2">{children}</div>
    </section>
  );
}

function Field({
  label,
  children,
  required,
  className,
}: {
  label: string;
  children: React.ReactNode;
  required?: boolean;
  className?: string;
}) {
  return (
    <div className={className}>
      <Label className="text-sm">
        {label}
        {required && <span className="text-accent"> *</span>}
      </Label>
      <div className="mt-2">{children}</div>
    </div>
  );
}

function SelectInput({ options }: { options: readonly string[] }) {
  return (
    <select className="w-full rounded-lg border border-border bg-card px-3 py-2.5 text-sm outline-none focus:border-accent">
      <option value="">Select…</option>
      {options.map((o) => (
        <option key={o}>{o}</option>
      ))}
    </select>
  );
}

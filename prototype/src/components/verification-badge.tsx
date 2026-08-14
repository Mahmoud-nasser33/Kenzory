import { cn } from "@/lib/utils";
import { verificationMeta, type Verification } from "@/lib/kenzory-data";

export function VerificationBadge({
  status,
  className,
  compact = false,
}: {
  status: Verification;
  className?: string;
  compact?: boolean;
}) {
  const meta = verificationMeta[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-wide",
        meta.tone,
        className,
      )}
    >
      <span className={cn("size-1.5 rounded-full", meta.dot)} />
      {compact ? meta.label.replace("Officially ", "").replace("Community ", "Community ") : meta.label}
    </span>
  );
}

export function LocalStoryBadge() {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/10 px-2.5 py-1 text-[11px] font-medium tracking-wide text-accent">
      <span className="size-1.5 rounded-full bg-accent" />
      Local Story
    </span>
  );
}

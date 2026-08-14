import { lazy, Suspense, useEffect, useState } from "react";
import type { Place } from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

// Leaflet touches `window` at import time, so the real map module is only
// loaded in the browser, after hydration.
const EgyptMapLeaflet = lazy(() => import("./egypt-map-leaflet"));

export type EgyptMapProps = {
  places: Place[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  className?: string;
  showControls?: boolean;
};

function MapSkeleton({ className }: { className?: string | undefined }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-border bg-sand pattern-geo",
        className,
      )}
    >
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs uppercase tracking-widest text-muted-foreground">
          Loading map…
        </span>
      </div>
    </div>
  );
}

export function EgyptMap(props: EgyptMapProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return <MapSkeleton className={props.className} />;

  return (
    <Suspense fallback={<MapSkeleton className={props.className} />}>
      <EgyptMapLeaflet {...props} />
    </Suspense>
  );
}

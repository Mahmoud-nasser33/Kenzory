import { useEffect, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { Minus, Plus, Crosshair, ArrowRight } from "lucide-react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { VerificationBadge } from "./verification-badge";
import type { Place } from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

const EGYPT_BOUNDS = L.latLngBounds([21.5, 24.5], [32.0, 37.0]);

function markerIcon(active: boolean) {
  return L.divIcon({
    className: "",
    html: `<span class="kz-pin${active ? " kz-pin-active" : ""}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

export default function EgyptMapLeaflet({
  places,
  selectedId,
  onSelect,
  className,
  showControls = true,
}: {
  places: Place[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  className?: string;
  showControls?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Record<string, L.Marker>>({});
  const [internalId, setInternalId] = useState<string | null>(null);
  const activeId = selectedId !== undefined ? selectedId : internalId;
  const selected = places.find((p) => p.id === activeId) ?? null;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current, {
      zoomControl: false,
      attributionControl: true,
      scrollWheelZoom: true,
      maxBounds: EGYPT_BOUNDS.pad(0.6),
      minZoom: 4,
      maxZoom: 17,
    });
    if (places.length === 1) {
      map.setView([places[0]!.lat, places[0]!.lng], 13);
    } else {
      map.fitBounds(EGYPT_BOUNDS, { padding: [16, 16] });
    }
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      maxZoom: 19,
    }).addTo(map);
    mapRef.current = map;
    // Tiles need a size recalculation once the container has settled.
    const t = window.setTimeout(() => map.invalidateSize(), 250);
    return () => {
      window.clearTimeout(t);
      map.remove();
      mapRef.current = null;
      markersRef.current = {};
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync markers with the current place list.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const next: Record<string, L.Marker> = {};
    for (const p of places) {
      const existing = markersRef.current[p.id];
      const marker =
        existing ??
        L.marker([p.lat, p.lng], { icon: markerIcon(false), title: p.name }).addTo(map);
      marker.off("click");
      marker.on("click", () => {
        setInternalId(p.id);
        onSelect?.(p.id);
      });
      next[p.id] = marker;
      delete markersRef.current[p.id];
    }
    for (const stale of Object.values(markersRef.current)) stale.remove();
    markersRef.current = next;
  }, [places, onSelect]);

  // Reflect selection in marker styling and recenter on it.
  useEffect(() => {
    for (const [id, marker] of Object.entries(markersRef.current)) {
      marker.setIcon(markerIcon(id === activeId));
      if (id === activeId) marker.setZIndexOffset(500);
      else marker.setZIndexOffset(0);
    }
    const map = mapRef.current;
    const place = places.find((p) => p.id === activeId);
    if (map && place) map.panTo([place.lat, place.lng], { animate: true });
  }, [activeId, places]);

  const reset = () => {
    const map = mapRef.current;
    if (!map) return;
    if (places.length === 1) map.setView([places[0]!.lat, places[0]!.lng], 13);
    else map.fitBounds(EGYPT_BOUNDS, { padding: [16, 16] });
  };

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-border bg-sand select-none",
        className,
      )}
    >
      <div ref={containerRef} className="absolute inset-0 z-0" />

      {showControls && (
        <div className="absolute right-4 top-4 z-[500] flex flex-col gap-1.5">
          <MapBtn onClick={() => mapRef.current?.zoomIn()} label="Zoom in">
            <Plus className="size-4" />
          </MapBtn>
          <MapBtn onClick={() => mapRef.current?.zoomOut()} label="Zoom out">
            <Minus className="size-4" />
          </MapBtn>
          <MapBtn onClick={reset} label="Recenter">
            <Crosshair className="size-4" />
          </MapBtn>
        </div>
      )}

      {selected && (
        <div className="absolute bottom-4 left-4 z-[500] w-[19rem] max-w-[calc(100%-2rem)] overflow-hidden rounded-xl border border-border bg-card shadow-[var(--shadow-lift)]">
          <img
            src={selected.image}
            alt={selected.name}
            loading="lazy"
            width={1200}
            height={800}
            className="h-28 w-full object-cover"
          />
          <div className="space-y-2 p-4">
            <VerificationBadge status={selected.verification} />
            <h4 className="font-display text-lg leading-tight">{selected.name}</h4>
            <p className="text-xs text-muted-foreground">
              {selected.city}, {selected.governorate} · {selected.category}
            </p>
            <Link
              to="/place/$placeId"
              params={{ placeId: selected.id }}
              className="inline-flex items-center gap-1.5 pt-1 text-sm font-medium text-accent hover:underline"
            >
              Explore Place <ArrowRight className="size-3.5" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function MapBtn({
  children,
  onClick,
  label,
}: {
  children: React.ReactNode;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className="flex size-9 items-center justify-center rounded-lg border border-border bg-card/90 text-foreground backdrop-blur transition-colors hover:bg-secondary"
    >
      {children}
    </button>
  );
}

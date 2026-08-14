import { Link } from "@tanstack/react-router";
import { MapPin, Clock, Bookmark } from "lucide-react";
import { VerificationBadge } from "./verification-badge";
import type { Place } from "@/lib/kenzory-data";
import { cn } from "@/lib/utils";

export function PlaceCard({ place, className }: { place: Place; className?: string }) {
  return (
    <Link
      to="/place/$placeId"
      params={{ placeId: place.id }}
      className={cn(
        "group surface-card block overflow-hidden rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:border-accent/30 hover:shadow-[var(--shadow-lift)]",
        className,
      )}
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <img
          src={place.image}
          alt={place.name}
          loading="lazy"
          width={1200}
          height={800}
          className="size-full object-cover transition-transform duration-700 group-hover:scale-105"
        />
        <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-stone/80 via-stone/20 to-transparent" />
        <div className="absolute left-3 top-3">
          <VerificationBadge
            status={place.verification}
            className="bg-card/90 shadow-[var(--shadow-soft)] backdrop-blur-md"
          />
        </div>
        <span className="absolute right-3 top-3 inline-flex size-8 items-center justify-center rounded-full bg-card/85 text-foreground opacity-0 backdrop-blur transition-opacity group-hover:opacity-100">
          <Bookmark className="size-4" />
        </span>
        <p className="absolute bottom-3 left-3 text-xs font-medium text-parchment">
          {place.distanceKm} km away
        </p>
      </div>

      <div className="space-y-2.5 p-5">
        <h3 className="font-display text-xl leading-snug text-foreground transition-colors group-hover:text-primary">
          {place.name}
        </h3>
        <p className="font-arabic text-sm text-muted-foreground" dir="rtl">
          {place.nameAr}
        </p>
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <MapPin className="size-3.5 text-accent" />
          {place.city}, {place.governorate}
        </div>
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 pt-1 text-xs">
          <span className="rounded-full bg-secondary px-2.5 py-1 font-medium text-secondary-foreground">
            {place.category}
          </span>
          <span className="text-muted-foreground">·</span>
          <span className="text-muted-foreground">{place.period}</span>
        </div>
        <div className="flex items-center gap-1.5 border-t border-border pt-3 text-xs text-muted-foreground">
          <Clock className="size-3.5" />~{place.visitMinutes} min visit · {place.approxDate}
        </div>
      </div>
    </Link>
  );
}

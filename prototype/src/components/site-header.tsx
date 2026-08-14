import { Link } from "@tanstack/react-router";
import { Search, Plus, Menu } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/explore", label: "Explore" },
  { to: "/map", label: "Map" },
  { to: "/discoveries", label: "Discoveries" },
  { to: "/add-place", label: "Add a Place" },
  { to: "/stories", label: "Stories" },
  { to: "/about", label: "About" },
] as const;

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-5">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="font-display text-lg leading-none">K</span>
          </span>
          <span className="flex flex-col leading-none">
            <span className="font-display text-xl tracking-tight">Kenzory</span>
            <span className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
              كنزوري
            </span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {nav.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="rounded-full px-3.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeProps={{ className: "bg-secondary text-foreground" }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <Link
            to="/explore"
            className="hidden items-center gap-2 rounded-full border border-border bg-card px-3.5 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground md:flex"
          >
            <Search className="size-4" />
            Search heritage sites
          </Link>
          <Button asChild size="sm" className="rounded-full">
            <Link to="/add-place">
              <Plus className="size-4" />
              <span className="hidden sm:inline">Add a Place</span>
            </Link>
          </Button>
          <Link
            to="/profile"
            className="hidden size-9 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-foreground sm:flex"
          >
            M
          </Link>
          <button
            className="flex size-9 items-center justify-center rounded-full border border-border lg:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            <Menu className="size-4" />
          </button>
        </div>
      </div>

      <div className={cn("border-t border-border lg:hidden", open ? "block" : "hidden")}>
        <nav className="mx-auto flex max-w-7xl flex-col p-3">
          {nav.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setOpen(false)}
              className="rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

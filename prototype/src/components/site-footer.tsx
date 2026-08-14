import { Link } from "@tanstack/react-router";

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-border bg-secondary/40">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="flex items-center gap-2.5">
            <span className="arch-mask flex size-9 items-center justify-center bg-primary text-primary-foreground">
              <span className="font-display text-lg leading-none text-accent">K</span>
            </span>
            <span className="font-display text-xl">Kenzory</span>
          </div>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
            Egypt has thousands of stories hiding in plain sight. Kenzory helps people find them,
            document them, and make sure they are not forgotten.
          </p>
          <p className="mt-6 text-xs text-muted-foreground">
            Prototype — all places, contributors, and stories shown are demo content.
          </p>
        </div>
        <div>
          <h4 className="font-display text-lg">Discover</h4>
          <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
            <li>
              <Link to="/explore" className="hover:text-foreground">
                Explore
              </Link>
            </li>
            <li>
              <Link to="/map" className="hover:text-foreground">
                Interactive map
              </Link>
            </li>
            <li>
              <Link to="/discoveries" className="hover:text-foreground">
                Discoveries feed
              </Link>
            </li>
            <li>
              <Link to="/stories" className="hover:text-foreground">
                Stories
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-display text-lg">Contribute</h4>
          <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
            <li>
              <Link to="/add-place" className="hover:text-foreground">
                Add a place
              </Link>
            </li>
            <li>
              <Link to="/profile" className="hover:text-foreground">
                Contributor profile
              </Link>
            </li>
            <li>
              <Link to="/about" className="hover:text-foreground">
                Verification standards
              </Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border py-6 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} Kenzory · A community heritage initiative
      </div>
    </footer>
  );
}

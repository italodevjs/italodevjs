<img src="assets/hero.svg" width="100%" alt="Italo — software developer"/>

<h3>Italo · Software Developer</h3>

I build and ship full-stack web products, and I run them in production — including
the parts that only show up after launch: payment webhooks, third-party OAuth,
egress bills and outages.

Based in Brazil, open to remote work.

---

### About

I work end to end: Next.js and TypeScript on the front, Postgres and route
handlers on the back, and whatever infrastructure the product turns out to need.
Security is where I pay the most attention — not as a label, but as the specific
questions of who can read this row, what happens if this URL points inward, and
whether this webhook can be replayed.

Most of what I know came from operating something real. My main project has been
down twice for reasons I had to diagnose and fix, and those two incidents taught
me more than any tutorial.

---

### Caliber — main project

**A biolink platform for creators.** One page holding every link, social account
and track, at `caliber.lol/username`. Built and operated solo.

**Live → [caliber.lol](https://caliber.lol)**

| | |
|:--|:--|
| **Stack** | Next.js 16 · React · TypeScript · Supabase Postgres · Tailwind · Cloudflare Workers + R2 |
| **Scale** | 34 API routes · 66 migrations · 42 RLS-protected tables · 89 test files |
| **Payments** | Stripe, NOWPayments and Ticto webhooks, with idempotent entitlement grants |
| **Integrations** | Discord, Spotify, Twitch, YouTube, Last.fm |

Things in it I'd want to be asked about:

- **An outage caused by a video banner.** Supabase cut the project off at 12.41 GB
  of egress against a 5 GB cap — taking the database and login down with it. Root
  cause was a 6.6 MB banner re-downloaded across 1,906 visits. I rejected "cache
  it better" and moved media to Cloudflare R2, where egress isn't billed, so the
  quota stops existing instead of becoming less likely to blow.
- **A read-through CDN with no migration.** The Worker copies each file to R2 on
  its first request. Every file leaves the origin exactly once, only files anyone
  opens get copied, and URLs already saved in profiles kept working.
- **SSRF protection on link previews.** The server resolves the hostname before
  fetching and refuses private, loopback and link-local addresses — closing
  `169.254.169.254` metadata reads.

---

### Stack

Only what I've actually shipped with.

| | |
|:--|:--|
| **Frontend** | TypeScript · React · Next.js (App Router, Server Components) · Tailwind CSS · Framer Motion |
| **Backend** | Node.js · Next.js Route Handlers · Zod validation |
| **Database** | PostgreSQL · Supabase · SQL migrations · row-level security |
| **Cloud** | Cloudflare Workers · R2 · Vercel · Docker |
| **Security** | OWASP Top 10 · SSRF defence · webhook signature verification · CSP, HSTS |
| **Tooling** | Git · GitHub Actions · Vitest · ESLint |

---

### Focus

Web application architecture · API design · authentication and authorisation ·
application security · database design · deployment and incident response

---

### Contact

[caliber.lol](https://caliber.lol) ·
[LinkedIn](https://www.linkedin.com/in/italodevjs) ·
[caetanoitalo60@gmail.com](mailto:caetanoitalo60@gmail.com)

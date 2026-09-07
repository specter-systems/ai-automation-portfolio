# AI Automation Portfolio — Claude, MCP & Python

I build AI agents and automation that run real business workflows: Claude MCP
connectors, Python data pipelines, and email/WhatsApp outreach systems.

**SPECTER SYSTEMS** · Doha, Qatar (GMT+3) · remote worldwide
[Site](https://specter-systems.github.io) · [Fiverr](https://www.fiverr.com/s/dDmB3YZ) · [Email](mailto:specter00000000@gmail.com)

---

## How to read this page

Work here is split into two honest buckets:

- **Shipped** — built, deployed, and running in production for a real organisation.
- **Demo** — built and working, but not yet deployed for a paying client. Numbers on
  these are my own estimates from testing, clearly marked. They are not client results.

I'd rather tell you which is which than have you find out later.

---

## Shipped

### Claude MCP connector suite
Three production MCP servers built on a reusable OAuth 2.1 server pattern.

- Combined **Instagram + Facebook** connector — **38 tools** covering publishing,
  comments, conversations, insights and moderation across both platforms
- **LinkedIn** connector — authenticated posting, image posts, profile and token status
- Shared auth layer, so a new platform is a config change rather than a rewrite

`Python` · `MCP` · `OAuth 2.1` · `Meta Graph API` · `LinkedIn API` · `Vercel`

### Lead generation pipeline
Bilingual (English/Arabic) company discovery across mapping and directory sources.

- Coordinate-grid + text search strategy for full geographic coverage
- SQLite store with de-duplication, stale-source pruning and an out-of-market gate
- Async rewrite tripled scraping throughput
- **60,000+ company records** with websites and phone numbers

`Python` · `asyncio` · `SQLite` · `Scraping` · `Data cleaning`

### Outreach engine & campaign dashboard
Multi-worker email agent plus WhatsApp Cloud API campaign flows.

- Worker queue for send throughput and retry handling
- WhatsApp carousel and flow templates for catalogue-style campaigns
- **9-view Next.js dashboard** for campaign state, contact routing and delivery status
- Spreadsheet-backed CRM so non-technical staff can work the pipeline

`Next.js` · `Node.js` · `WhatsApp Cloud API` · `Google Sheets API`

### Multi-brand analytics dashboard
Reporting dashboard covering **15 brands** for a retail group.

- Adjustable reporting periods, PDF report upload and storage
- Role-based authentication
- Scheduled keepalive job via GitHub Actions

`Next.js` · `Supabase` · `Auth` · `GitHub Actions`

### Commerce & ERP integration
Custom Shopify app bridging a live storefront to an **Odoo v19** backend.

- OAuth app install flow, custom distribution
- Catalogue hygiene: duplicate SKU resolution, handle repair after bulk imports
- Multi-domain consolidation and regulatory compliance footer

`Shopify API` · `Odoo v19` · `OAuth`

---

## Demos

Built and working. Not yet run for a paying client — figures are my own test estimates.

### PDF data extractor
Invoice and financial-document extraction for accounting workflows.

- Documents in via email or API
- Claude extracts structured fields — vendor, amount, date, line items
- Writes to Google Sheets, flags anomalies for human review

*Estimated saving in my own testing: several hours per week at typical small-firm volume.
Not a measured client result.*

`Claude API` · `n8n` · `Python`

### Meeting summariser & action tracker
Transcript in, executive summary and assigned action items out.

- Accepts Zoom/Teams/Meet transcripts
- Claude generates summary plus owner-assigned action items
- Creates Notion tasks and sends deadline follow-ups

*Estimated to remove most post-meeting admin time. Not a measured client result.*

`Claude API` · `n8n` · `Notion API`

### Lead qualification bot
Qualifies inbound leads before they reach the CRM.

- Scores and routes leads against defined criteria
- Pushes qualified leads to Slack/Telegram and the sheet, drops the rest

*Built as a demo. No client conversion data to report.*

`Claude API` · `n8n` · `Telegram API` · `Google Sheets API`

---

## Stack

| Area | Tools |
|---|---|
| AI & agents | Claude API, Model Context Protocol, n8n |
| Backend | Python (asyncio), Node.js, SQLite, Postgres |
| Frontend & deploy | Next.js, TypeScript, Supabase, Vercel, GitHub Actions |
| Platform APIs | Meta Graph, WhatsApp Cloud, LinkedIn, Shopify, Odoo, Google Sheets |

## How to engage

| Engagement | What you get | From |
|---|---|---|
| Bug fix / site repair | One defined defect diagnosed and fixed, ordered through Fiverr with buyer protection | **$15** |
| Automation build | One workflow end to end — scoped, built, deployed, documented | **$300** |
| Custom MCP connector | A Claude connector for your tool: auth, tools, deployment, maintenance window | **$500** |
| Ongoing retainer | Monthly capacity for maintenance, extensions and new automation | Let's talk |

Fixed scope, fixed price, agreed before work starts. First engagements are deliberately
small — you should be able to test whether I'm worth hiring without a large commitment.

## Contact

- Email — [specter00000000@gmail.com](mailto:specter00000000@gmail.com)
- Fiverr — [fiverr.com/s/dDmB3YZ](https://www.fiverr.com/s/dDmB3YZ)
- Telegram — [@specter0bot](https://t.me/specter0bot)

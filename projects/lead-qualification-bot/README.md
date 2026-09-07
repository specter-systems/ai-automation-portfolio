# Lead qualification bot — design only

**Status:** Not built. No code in this folder.
**Intended stack:** Claude API · n8n · Telegram · Google Sheets

## What it would do

Qualify inbound leads in conversation before they reach a CRM.

1. Lead submits a form on the site
2. Bot opens a conversation over Telegram or Slack
3. Asks qualifying questions — budget, timeline, needs
4. Scores the lead against defined criteria (hot / warm / cold)
5. Routes qualified leads to the CRM, archives cold ones
6. Notifies the sales team on a hot lead

## Results

None. Nothing has been built, so there is nothing to measure.

An earlier version of this file listed conversion and time-saving figures. They were
projections, not measurements, and they should not have been written as results. They have
been removed. Numbers appear in this portfolio only when they describe something that was
actually built, and client outcome figures only when a client has agreed to them.

## If you want this built

The pieces that need deciding before it is worth writing: what your qualifying criteria
actually are, where the leads land today, and who gets woken up for a hot one. That
conversation is most of the work; the automation is the easy half.

See [`projects/invoice-extractor`](../invoice-extractor) for a workflow of mine that *is*
built, with tests you can run.

---
*Part of the [Specter Systems](https://specter-systems.github.io) portfolio.*

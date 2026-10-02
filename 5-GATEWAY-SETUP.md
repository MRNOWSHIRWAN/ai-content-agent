# GhostScribe gateway preview

The gateway is authenticated and fails closed until DEVICE_TOKEN, GEMINI_API_KEY and a D1 QUOTA binding are configured. It accepts explicitly consented non-personal online chat and curated public research/study requests. It does not attach phone notes, reminders, profile or chat history. Typed online questions reach Google free Gemini and can be reviewed/used to improve products. Do not type private information.

Free-only: no billing activation, no paid fallback. D1 schema: CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0);. Daily online-request cap is 30 per UTC day. Production tests remain required.

This is source preview, not a finished always-available assistant. Android installation, reminder/reboot behavior and model responses are not yet verified. The existing content CLI remains unchanged by this initial gateway publication.

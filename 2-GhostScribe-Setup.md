# GhostScribe 0.1 preview setup

This is a development preview, not a finished always-on personal agent. Local notes and one-time reminders work without an online account. A protected gateway is deployed for the owner. Other users must deploy their own gateway and keys. This source bundle does not include pairing credentials.

## Privacy
Private notes and reminder text stay in Android app-private storage. Android automatic backup is disabled. Web content cannot make network requests. The native bridge constructs only fixed topic/action/language requests. The server rejects any extra user text or private fields. Study/research uses curated topics. Online chat sends the question you explicitly type after a first-send consent dialog. Google free-tier content may be reviewed/used to improve products. Do not type personal information. No local notes, reminders, profile or history are automatically attached. A warning does not technically prevent you from typing personal data. Exports are private unencrypted JSON, without pairing credentials.

## Owner cloud setup
1. Use your own Cloudflare Free account. Do not select a paid plan or add billing automatically.
2. Create a D1 database named ghostscribe-quota. Run gateway/schema.sql. This holds only day and request count, not chat or notes.
3. Set the database ID in gateway/wrangler.jsonc.
4. Deploy gateway/worker.mjs and its catalog modules together using Wrangler or a module-capable deployment workflow.
5. Add GEMINI_API_KEY as a secret, not a plain source-code variable. Use a Google project without active billing for free-only operation. Gemini 3.1 Flash-Lite passed live testing on October 2; model availability/quota must be rechecked for your project, with no paid fallback.
6. Generate a unique random DEVICE_TOKEN of at least 32 characters and set it as a server secret. Pair the Android app with the deployed HTTPS address and this token. Never share the token publicly.
7. Test unauthorized requests (401), extra text fields (400), generic lesson response, source-linked report, and daily quota (429). Model failures should leave local tools usable.

The app's quota allows up to 30 online lessons/reports per UTC day. A report uses only catalog sources and limited text excerpts. It is not broad web search or independent fact verification. Failed model calls may count toward the cap. Cloudflare free CPU limits need production testing before suitability is confirmed.

## Install and local checks
Android 8 or later. The compiled current APK is unsigned. The older development preview uses a development signing key, not a durable owner release signer. Do not treat it as the long-term installed version until signing continuity is settled.
1. Install APK and open it.
2. Add a note, close/reopen app and confirm it remains.
3. In Reminders, press Enable permissions. Android 13+ asks for notification permission. Android 12+ may require a second press for Alarms & reminders access.
4. Add a reminder two minutes ahead. Leave the app and verify a notification.
5. Try without internet, after reboot, with notification permission denied, and with alarm access denied. Without alarm access pings can be delayed. Force-stop/offline phone restrictions can prevent alerts.
6. Mark done and check its timestamp. Export JSON, then restore it after reviewing the replace confirmation. Test on disposable data first.
7. Use the phone's Clock for critical alarms until actual phone behavior has been checked.

## Build and signing
Set JAVA_HOME (JDK 17), ANDROID_JAR (SDK platform 35 android.jar), BUILD_TOOLS (SDK 35.0.0) and run android/build.sh. Supply SIGNING_KEYSTORE for owner release signing. Preserve that private key securely: losing or changing it prevents normal updates and may force reinstall. Do not commit keystores to GitHub.

## Not yet built
Recurring/snoozed reminders, private companion chat, broad multi-hop search, full article relevance extraction, designed carousel images, auto-posting, account integrations, cloud sync and on-device LLM inference. Existing Python content CLI remains available with modernized SDK adapter; it has not been runtime-tested against a live key here.

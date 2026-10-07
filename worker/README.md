# Lead proxy for Follow Up Boss

The website posts both forms to this small Cloudflare Worker. The Worker validates the lead and creates an
event in Follow Up Boss, which adds the person to your CRM with tags and the full qualification details in the note.
The API key stays on the server and never appears in the site's HTML.

## Setup (about 10 minutes)
1. In Follow Up Boss go to Admin > API and create an API key.
2. Optional but recommended: register the system at https://apps.followupboss.com/system-registration
   (name `GBHomeRentals`) and keep the System Key it gives you.
3. Install Wrangler and deploy:
   ```
   cd worker
   npx wrangler login
   npx wrangler secret put FUB_API_KEY        # paste the API key when prompted
   npx wrangler secret put FUB_SYSTEM_KEY     # optional, from step 2
   npx wrangler deploy
   ```
4. Edit `ALLOWED_ORIGINS` in `wrangler.toml` to your live domain before deploying.
5. Copy the deployed URL (https://gb-home-rentals-leads.<account>.workers.dev) into `FORM_ENDPOINT` in `index.html`.

## What lands in Follow Up Boss
- Qualification form: event type `Registration`, source `GB Home Rentals Website`, property address, tags such as
  `Owner Qualification`, `Okaloosa County`, `Interest: Repairs`, and every answer in the note.
- Info form: event type `General Inquiry`, tagged `Owner Inquiry`.
Set up an Action Plan or Smart List in Follow Up Boss keyed on the `GB Home Rentals` tag to route and follow up automatically.

## Address autocomplete
In Google Cloud, enable **Places API (New)** and **Maps JavaScript API**, create an API key, restrict it to your site's
domain under HTTP referrers, and paste it into `GOOGLE_MAPS_API_KEY` in `index.html`.

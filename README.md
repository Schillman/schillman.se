# schillman.se

The hub site at [schillman.se](https://schillman.se). Static files, no build step. Deployed on Netlify.

The Diablo IV Season 14 Farming Ledger at `d4.schillman.se` is a separate repo, [Schillman/farming-ledger](https://github.com/Schillman/farming-ledger).

## Files

| File | What it is |
|---|---|
| `index.html` | The homepage. Design tokens are copied from the ledger so the two sites match. |
| `privacy.html` | Privacy and cookie policy covering this domain and its subdomains. Required by the AdSense terms. |
| `ads.txt` | AdSense authorized seller record. Must live on the root domain even though the ads run on the subdomain. |

## Rules that are not obvious from the code

- **No ad code on `index.html`.** The homepage is a hub, and AdSense rejects ads on navigation pages with little content. Ads run only on `d4.schillman.se`. This was the reason for the first policy strike.
- Keep `privacy.html` accurate. If analytics or another ad provider is ever added, update that page and the date at the top of it in the same commit.
- No em dashes and no curly quotes in copy, matching the ledger.
- One accent color (ember `#ff5a36`). Any new text color gets its WCAG contrast checked against its real background, 4.5:1 for normal text.

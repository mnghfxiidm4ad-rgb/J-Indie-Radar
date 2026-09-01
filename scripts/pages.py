"""Static policy pages required for AdSense / E-E-A-T."""

from datetime import date

UPDATED = date.today().isoformat()

PRIVACY_HTML = """
<p>J-Indie Radar ("we", "us", or "the site") is an independent editorial website that publishes English-language dossiers on Japanese indie games. This Privacy Policy explains what information we collect, how advertising and analytics partners use cookies, and what choices you have. It is written to meet Google AdSense disclosure requirements and to be readable by a human, not only a lawyer.</p>

<h2>1. Who is responsible</h2>
<p>J-Indie Radar is an independently operated static website. For privacy questions, advertising opt-outs, or data requests, use the contact form or email address published on our <a href="contact.html">Contact</a> page. We will respond within a reasonable period.</p>

<h2>2. What this site collects</h2>
<p>The public pages themselves are static HTML. We do not run a first-party user account system and we do not ask you to create a login. Limited information may still be processed:</p>
<ul>
  <li><strong>Information you send us.</strong> If you email us or submit a contact / review-request form, we receive the fields you choose to provide (typically name or handle, email address, message, and optional game title). We use that only to reply and to keep a record of correspondence.</li>
  <li><strong>Technical logs via third parties.</strong> Hosting providers (for example GitHub Pages or Cloudflare) and analytics / advertising partners may process IP address, browser type, device type, referring URL, pages viewed, and approximate location derived from IP. We do not sell this information.</li>
</ul>

<h2>3. Cookies and similar technologies</h2>
<p>Cookies are small text files stored on your device. Some are set by us (if we add a preference cookie in the future); many are set by third parties that serve ads or measure traffic. You can refuse non-essential cookies in your browser settings. Blocking cookies may reduce personalization of ads but will not remove access to our articles.</p>

<h2>4. Google AdSense and third-party advertising</h2>
<p>This site uses Google AdSense to display advertisements. Google and other third-party vendors use cookies to serve ads based on a user's prior visits to this website and other websites. Google's use of advertising cookies enables it and its partners to serve ads to our users based on their visit to this site and/or other sites on the Internet.</p>
<p>Third-party vendors, including Google, use cookies to serve ads on this site. These cookies may include the DoubleClick / Google advertising cookie, which is used to serve ads and measure interactions. Personalized advertising may use information about your browsing activity on this site and elsewhere, subject to Google's policies and your ad settings.</p>
<ul>
  <li>Users may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener noreferrer">Google Ads Settings</a>.</li>
  <li>Alternatively, users can opt out of some third-party vendor cookies by visiting <a href="https://optout.aboutads.info/" rel="noopener noreferrer">www.aboutads.info</a> and/or the Network Advertising Initiative opt-out page at <a href="https://optout.networkadvertising.org/" rel="noopener noreferrer">optout.networkadvertising.org</a>.</li>
  <li>Google's advertising policies and partner information are described at <a href="https://policies.google.com/technologies/ads" rel="noopener noreferrer">Google Advertising</a> and <a href="https://policies.google.com/privacy" rel="noopener noreferrer">Google Privacy Policy</a>.</li>
</ul>
<p>We do not control the cookies set by Google or other ad partners. Those companies act as independent controllers of the data they collect through their tags. If we enable additional ad networks in the future, we will update this page and identify them.</p>

<h2>5. Google Analytics and similar measurement</h2>
<p>We may use Google Analytics (or a comparable privacy-respecting analytics tool) to understand aggregated readership: which dossiers are opened, which genres are filtered, and how people arrive from search. Google Analytics uses cookies to distinguish sessions. Where Analytics is installed, IP anonymization is enabled when the product supports it. You can opt out of Google Analytics with the <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener noreferrer">Google Analytics Opt-out Browser Add-on</a>.</p>
<p>Analytics data is used to improve editorial planning (for example, covering more horror titles if those dossiers are widely read). It is not used to identify you as a named individual.</p>

<h2>6. Legal bases (EEA / UK readers)</h2>
<p>If you are in the European Economic Area or the United Kingdom, we process personal data on these bases: (a) legitimate interests in running an editorial site, measuring audience, and showing advertising to fund the work; (b) consent, where required for non-essential cookies and personalized ads; (c) performance of a request you initiate, when you contact us. You may have rights to access, rectify, erase, restrict, or object to processing, and to lodge a complaint with a supervisory authority.</p>

<h2>7. Children</h2>
<p>J-Indie Radar is written for a general audience of adult and teen game players. We do not knowingly collect personal information from children under 13 (or the equivalent age in your country). Some games we cover contain horror, violence, or mature themes; parental guidance is the reader's responsibility.</p>

<h2>8. Retention and security</h2>
<p>Contact emails are kept only as long as needed to handle the request and any follow-up. Hosting and partner logs follow those providers' retention schedules. No method of transmission over the Internet is perfectly secure; we use reputable static hosting and HTTPS where the host provides it.</p>

<h2>9. International transfers</h2>
<p>Our hosts and Google services may process data in the United States and other countries. If you read the site from outside those countries, you understand that your information may be transferred internationally under the safeguards those providers publish.</p>

<h2>10. Changes</h2>
<p>We will update this Privacy Policy when our advertising, analytics, or contact practices change. The "last updated" date at the top of the page is the source of truth. Material changes to cookie or advertising practice will be reflected here before those tags go live whenever practical.</p>
"""

ABOUT_HTML = """
<p>J-Indie Radar exists because Steam's Japanese indie catalog is full of games that overseas players bounce off for the wrong reasons: a Japanese-only store description, a meme screenshot, or a "Overwhelmingly Positive" score with no explanation of <em>why</em> Japanese players keep recommending it. We write long, structured English dossiers so that a player in São Paulo, Warsaw, or Toronto can decide whether a Japanese indie is worth their weekend.</p>

<h2>Mission</h2>
<p>We scan Steam for Japan-made indie, doujin, and small-studio games — JRPG, horror, action, roguelite, shmup, and adjacent genres — and publish original analysis that answers four questions Google's "thin content" rules (and any serious reader) actually care about:</p>
<ul>
  <li>What is this game, mechanically, in 150–200 words that are not a paraphrased store blurb?</li>
  <li>What is unique about the systems loop once you are past the first thirty minutes?</li>
  <li>Why did Japanese reviews and social posts treat it as a big deal?</li>
  <li>Can you play it without Japanese fluency, and what will you miss?</li>
</ul>

<h2>Editorial independence</h2>
<p>J-Indie Radar is not a Steam publisher, not a localization house, and not a marketing blog. Developers may send review keys or factual corrections through our contact page. A key never buys a score, a ranking, or a softened language-barrier warning. We do not sell "featured placement." If we ever use affiliate links, they will be labeled on the page that contains them. Store buttons currently go to the public Steam page.</p>

<h2>Curatorial process (how a game gets a dossier)</h2>
<ol>
  <li><strong>Japan-origin filter.</strong> We prioritize titles whose primary developer or creative director is based in Japan, including doujin circles and micro-studios that ship on Steam via PLAYISM, Playism-adjacent labels, self-publishing, or small Japanese publishers. Fangames are eligible when the <em>studio</em> is Japanese; we label them as unofficial when they are.</li>
  <li><strong>Steam evidence.</strong> We pull store metadata (tags, supported languages, release date) and a sample of Japanese-language user reviews. We do not copy reviews. We use them as a signal of what Japanese players praise, complain about, or warn newcomers regarding.</li>
  <li><strong>Design reading.</strong> Each dossier includes a systems deep-dive: resource loops, fail states, information design, and how the game teaches (or refuses to teach). This is original editorial writing, not an LLM dump of the store page.</li>
  <li><strong>Language-barrier grading.</strong> We grade None / Low / Medium / High with operational detail (can you menu, can you solve text puzzles, is combat readable from animation). This is the page overseas players actually need and almost never get from English coverage.</li>
  <li><strong>Human editorial pass.</strong> Automated tooling may draft structure from public Steam data and Japanese review clusters. A human editor is responsible for the published claim set, names, and the final language-barrier grade. We would rather publish fewer dossiers than a pile of interchangeable blurbs.</li>
</ol>

<h2>Use of AI tools (transparency)</h2>
<p>We may use large language models as a <em>research assistant</em>: clustering Japanese review themes, checking that a draft hits the required sections, or translating a phrase for verification. AI is not allowed to be the sole author of a published dossier. Thin, repetitive, or hallucinated pages are an editorial failure and an AdSense risk; our process is built to reject them. Factual game systems are checked against the Steam page, patch notes, and (where we have played the title) first-hand notes.</p>

<h2>E-E-A-T: what we claim, and what we do not</h2>
<p><strong>Experience.</strong> Dossiers distinguish first-hand play notes from synthesis of Japanese player discussion. When we have not finished a title, we say so by focusing on systems that are observable from public build information and review consensus rather than inventing late-game plot.</p>
<p><strong>Expertise.</strong> The site specializes in Japanese indie design vocabulary (doujin action, RPG Maker horror grammar, shmup rank systems, Metroidvania exploration opacity). We would rather be precise about one scene than generic about "this game has great atmosphere."</p>
<p><strong>Authoritativeness.</strong> We cite the Steam store as the commercial source of truth for price, language list, and developer name. Rankings on this site are editorial, not an official Japanese chart.</p>
<p><strong>Trust.</strong> Corrections are welcome. If a developer or player shows that a language-barrier grade is wrong, we update the dossier and change the timestamp. We do not host game files, cracks, or leaked assets.</p>

<h2>Who we are</h2>
<p>J-Indie Radar is operated as a small independent editorial project. We write in English because that is the gap: Japanese communities already know these games, and English store pages often do not. For press, correction, or "please cover our game" requests, use <a href="contact.html">Contact</a>.</p>
"""

CONTACT_HTML = """
<p>Use this page to reach the editorial desk. We read every serious message. We cannot reply to every Steam key offer on the same day, but we do log them against our curatorial queue.</p>

<div class="contact-grid">
  <div class="contact-card">
    <h2>How to reach us</h2>
    <p>Primary contact is the Google Form on this page, also available at <a href="https://forms.gle/Eh6uh7b2BC6P3qEz6" rel="noopener noreferrer">forms.gle/Eh6uh7b2BC6P3qEz6</a>.</p>
    <p>Please include a Steam store URL, the languages the build currently supports, whether a review key is offered, and a one-paragraph note on why Japanese players are talking about the game <em>now</em>.</p>
    <h2>What we can help with</h2>
    <ul>
      <li>Factual corrections on a published dossier (names, dates, language support).</li>
      <li>Review / coverage requests from Japanese indie developers and publishers.</li>
      <li>Reader questions about language-barrier grades.</li>
      <li>Privacy and cookie requests described in the Privacy Policy.</li>
    </ul>
    <h2>What we will not do</h2>
    <ul>
      <li>Host or link to pirated copies, "free download" mirrors, or leaked source.</li>
      <li>Accept payment for a guaranteed article or a guaranteed positive grade.</li>
      <li>Mediate player-versus-developer disputes on Steam.</li>
    </ul>
  </div>
  <div>
    <h2>Contact form</h2>
    <p><a class="btn btn-primary" href="https://forms.gle/Eh6uh7b2BC6P3qEz6" rel="noopener noreferrer">Open the form in a new tab</a></p>
    <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfqzO3DXp5V8f8FdWfNxgAk_bgJMSXIcMlWHQiFvQkuTMMukA/viewform?embedded=true" width="100%" height="720" style="border:0;border-radius:16px;min-height:720px;margin-top:16px;" title="J-Indie Radar contact form"></iframe>
  </div>
</div>
"""

DISCLAIMER_HTML = """
<p>J-Indie Radar is an independent editorial website. Please read this page before treating any dossier as official information from Steam, Valve, or a game's developer.</p>

<h2>1. No affiliation</h2>
<p>This site is not affiliated with, endorsed by, or sponsored by Valve Corporation, Steam, PLAYISM, or any developer, publisher, or character-rights holder named in our articles, unless a specific article states otherwise. Steam and the Steam logo are trademarks of Valve Corporation. Game names, character names, logos, screenshots, and header artwork remain the property of their respective owners. Header images are loaded from Steam's public CDN for identification and commentary.</p>

<h2>2. Fan works and unofficial titles</h2>
<p>Some dossiers cover doujin or unofficial games that use settings associated with other creators (for example, Touhou Project fangames). Those articles describe a specific commercial Steam build. They are not official products of the original rights holder unless we explicitly say they are. If a title is removed from Steam or a rights holder requests a correction, we will update or unpublish the page.</p>

<h2>3. Editorial opinions</h2>
<p>Vibe labels, language-barrier grades, difficulty notes, playtime estimates, and "why it is trending" sections are opinions and synthesis. They can be wrong as patches ship, as fan-translation tools improve, or as a Japanese social spike fades. Playtime assumes a first completion for a player of average genre literacy, not 100% achievement hunting unless stated.</p>

<h2>4. Accuracy and sources</h2>
<p>Store facts (developer name, listed languages, current tags) are taken from public Steam metadata at build time and may lag behind a live store page. Japanese review themes are paraphrased and aggregated; we do not reproduce Steam user reviews verbatim. You should confirm price, age rating, hardware requirements, and current language support on the official Steam page before you buy.</p>

<h2>5. Adult, horror, and sensitive content</h2>
<p>Several games on the radar include sudden violence, ghost imagery, child-endangerment themes in fiction, or psychological horror. We do not try to replace an age rating. If a work is likely to distress, the dossier will say so in the vibe or audience section. Reader discretion applies.</p>

<h2>6. No downloads, no cheats, no account help</h2>
<p>We do not host game binaries, mods that include copyrighted assets, cracked copies, or Steam account credentials. We do not provide instructions for bypassing Steam DRM, region locks, or payment systems. Buy games from legitimate storefronts.</p>

<h2>7. Liability</h2>
<p>Articles are provided "as is" for informational and entertainment purposes. To the fullest extent permitted by law, J-Indie Radar is not liable for purchase decisions, wasted playtime, spoilers you chose to read, or third-party ads displayed by Google or other networks. External links (including Steam and Google policy pages) are outside our control.</p>

<h2>8. Takedown and correction</h2>
<p>Rights holders who believe a page misuses their marks, or developers who find a factual error, should write to the address on our Contact page with a URL and a specific correction. We will review in good faith. Privacy requests are handled under the Privacy Policy.</p>
"""


def page_defs() -> list[dict]:
    return [
        {
            "slug": "privacy",
            "nav": "privacy",
            "kicker": "Legal",
            "heading": "Privacy Policy",
            "title": "Privacy Policy — J-Indie Radar",
            "description": "How J-Indie Radar uses cookies, Google AdSense, Google Analytics, and contact data.",
            "body": PRIVACY_HTML,
        },
        {
            "slug": "about",
            "nav": "about",
            "kicker": "E-E-A-T",
            "heading": "About Us & Editorial Policy",
            "title": "About Us & Editorial Policy — J-Indie Radar",
            "description": "Mission, curatorial process, AI transparency, and editorial independence of J-Indie Radar.",
            "body": ABOUT_HTML,
        },
        {
            "slug": "contact",
            "nav": "contact",
            "kicker": "Desk",
            "heading": "Contact Us",
            "title": "Contact Us — J-Indie Radar",
            "description": "Contact J-Indie Radar for corrections, review requests, and privacy questions.",
            "body": CONTACT_HTML,
        },
        {
            "slug": "disclaimer",
            "nav": "disclaimer",
            "kicker": "Legal",
            "heading": "Terms & Disclaimer",
            "title": "Terms & Disclaimer — J-Indie Radar",
            "description": "Affiliation, trademark, fan-work, and liability disclaimer for J-Indie Radar.",
            "body": DISCLAIMER_HTML,
        },
    ]

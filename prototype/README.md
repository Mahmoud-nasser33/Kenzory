# Kenzory Heritage Atlas

Design a high-fidelity modern web application prototype called "Kenzory".

Kenzory is a community-driven digital heritage initiative dedicated to discovering, documenting, and preserving Egypt's lesser-known historical and cultural heritage.

CORE CONCEPT:

Kenzory allows people across Egypt to discover hidden historical places that are often unknown to tourists and even local residents. Users can explore an interactive map of Egypt, discover nearby heritage sites, read their history and stories, view photos, and contribute new places and information to the community.

The product should feel like a serious real-world Egyptian heritage platform, NOT a generic tourism website.

TARGET USERS:

- Egyptian locals who want to discover places around them

- Travelers exploring lesser-known areas of Egypt

- History and archaeology enthusiasts

- Photographers and explorers

- Researchers and students

- Local communities who want to document their heritage

DESIGN DIRECTION:

- Premium, modern, elegant, and highly trustworthy

- Strong Egyptian cultural identity without looking old-fashioned

- Minimal and clean interface

- Warm archaeological-inspired visual language

- Use subtle references to Egyptian architecture, stone textures, ancient maps, Arabic geometric patterns, and traditional Egyptian visual elements

- Avoid excessive pyramids, pharaoh illustrations, hieroglyphics, or stereotypical tourist imagery

- The design should communicate DISCOVERY, HISTORY, COMMUNITY, and PRESERVATION

- Responsive desktop-first design that can later adapt to mobile

COLOR DIRECTION:

Use an elegant heritage-inspired palette:

- warm sand / parchment

- deep charcoal

- muted terracotta

- dark earthy green or olive

- subtle gold accents

Keep the interface clean and modern rather than overly colorful.

TYPOGRAPHY:

Use a modern highly readable sans-serif for the interface.

Use a refined serif/display font sparingly for historical titles and major headings.

Support both English and Arabic interfaces.

MAIN NAVIGATION:

- Explore

- Map

- Discoveries

- Add a Place

- Stories

- About

HOMEPAGE:

Hero section:

Large statement:

"Discover the Egypt You Never Knew."

Supporting text:

"Explore forgotten places, hidden landmarks, local stories, and cultural heritage documented by the people who know them."

Primary CTA:

"Explore Hidden Places"

Secondary CTA:

"Share a Discovery"

Hero visual:

An elegant interactive map of Egypt with subtle location markers representing hidden heritage sites.

Below the hero:

A section titled:

"Hidden Around You"

Show several lesser-known Egyptian heritage locations in attractive cards.

Each card should contain:

- authentic-looking location image

- place name

- governorate

- heritage category

- approximate historical period

- distance

- verification status

Example:

"Historic Mosque of ..."

"Minya, Egypt"

"Islamic Heritage · Ottoman Period"

"Verified"

MAP EXPERIENCE:

Create a dedicated interactive Egypt map.

Users can:

- zoom and pan across Egypt

- search locations

- filter by category

- filter by historical period

- filter by governorate

- find places near their current location

Categories:

- Ancient Egyptian

- Islamic Heritage

- Coptic Heritage

- Ottoman

- Modern Egyptian History

- Traditional Architecture

- Cultural Heritage

- Unknown / Local Heritage

Each map marker opens a compact preview card with:

- image

- name

- location

- category

- verification status

- "Explore Place" button

PLACE DETAILS PAGE:

Create a rich detail page for a historical location.

Include:

1. Large image gallery

2. Place name in Arabic and English

3. Location

4. Historical period

5. Category

6. Interactive map

7. Historical description

8. "Why it matters"

9. Local stories

10. Architecture / features

11. Historical timeline

12. Photo gallery

13. Sources and references

14. Verification status

15. Contributor information

16. Nearby historical places

Important:

Clearly distinguish between verified historical information and community-submitted stories.

Example badges:

- Officially Verified

- Community Verified

- Under Review

- Local Story

COMMUNITY CONTRIBUTION:

Create an "Add a Place" flow.

Users can submit:

- Place name

- Arabic name

- Location on map

- Governorate

- Category

- Historical period

- Estimated date

- Description

- Why the place is important

- Local stories

- Photos

- References / sources

- Additional notes

Show a clear message:

"Help preserve a piece of Egypt's history."

After submission:

"Your discovery has been submitted for review."

USER PROFILE:

Create contributor profiles showing:

- Profile photo

- Name

- Bio

- Places discovered

- Contributions

- Photos

- Verified discoveries

- Saved places

- Reputation / contributor level

Example:

"Mahmoud"

"Heritage Explorer"

"17 Discoveries"

"11 Verified"

"83 Photos"

Create a reputation system based on contribution quality rather than simply the number of submissions.

DISCOVERIES FEED:

Create a community feed where users can see recently added places and stories.

Cards can show:

"New Discovery"

"An abandoned Ottoman-era structure discovered in..."

"Added by Ahmed"

"2 days ago"

Users can:

- like

- save

- comment

- share

- report inaccurate information

SEARCH:

Create powerful search functionality.

Users should be able to search:

- place name

- governorate

- city

- category

- historical period

- contributor

- nearby locations

Include suggested searches such as:

"Hidden places near Luxor"

"Historic mosques in Minya"

"Coptic heritage near Cairo"

"Unknown historical places in Upper Egypt"

DISCOVERY EXPERIENCE:

Create a section called:

"Hidden Gems Near You"

Show:

"You have 8 heritage sites within 30 km."

Include distance, estimated visit time, category, and historical period.

Also create:

"Explore by Governorate"

Show all Egyptian governorates as an elegant visual grid/map.

VERIFICATION SYSTEM:

The platform must prioritize historical accuracy.

Every place should have a visible verification state:

GREEN:

Officially Verified

BLUE:

Community Verified

YELLOW:

Under Review

GRAY:

Unverified

Allow contributors to submit sources such as:

- Ministry of Tourism and Antiquities

- archaeological records

- academic publications

- books

- historical archives

- local documentation

Do not present unverified claims as established historical facts.

STORIES:

Create a dedicated "Stories" section focused on the human side of heritage.

Examples:

"The Mosque Everyone in the Village Forgot"

"An Abandoned Railway Station With 120 Years of History"

"The Story Behind an Ancient Craft in Upper Egypt"

This section should feel editorial and immersive.

DESIGN DETAILS:

Use:

- large photography

- elegant cards

- subtle shadows

- rounded but not overly playful UI

- smooth hover interactions

- map-based discovery

- subtle animations

- clean spacing

- strong visual hierarchy

- accessible contrast

The interface should feel comparable in quality to a modern startup such as Airbnb, Atlas Obscura, or Google Arts & Culture, while having a distinct Egyptian cultural identity.

IMPORTANT:

Do NOT make it look like a traditional government tourism website.

Do NOT make it look like a generic travel booking platform.

Do NOT focus only on famous monuments.

The central idea is discovering and preserving the LESSER-KNOWN heritage of Egypt through community contributions.

The prototype should demonstrate a complete user journey:

Discover → Explore Map → Open Place → Learn Its Story → Save/Share → Add a New Place → Community Verification.

Create realistic sample Egyptian locations and content for the prototype, but clearly mark fictional/demo data where appropriate.

Overall feeling:

"Egypt has thousands of stories hiding in plain sight. Kenzory helps people find them, document them, and make sure they are not forgotten."

## Development

You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```

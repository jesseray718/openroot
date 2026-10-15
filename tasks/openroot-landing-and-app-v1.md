# Task: OpenRoot Landing Page, Layout, and Application Upgrade v1

Upgrade the OpenRoot web presence and application shell into a modern, professional,
catchy, and developer-friendly interface.

## Product direction

OpenRoot is a local-first, provenance-bearing knowledge and collaboration system for
open hardware, open-source software, evidence, and distributed computing.

The interface should feel:
- Professional and credible
- Modern and clean
- Fast and lightweight
- Developer-oriented
- Open-source native
- Suitable for both technical and non-technical visitors

## Landing page requirements

Create or upgrade the homepage with these sections:

1. Hero
   - Clear headline: “Local-first knowledge. Verifiable collaboration.”
   - Short explanation of OpenRoot.
   - Primary call to action: “Explore OpenRoot”
   - Secondary call to action: “View GitHub”

2. Value propositions
   - Local-first evidence pods
   - SHA-256 provenance and reproducible artifacts
   - Searchable knowledge with SQLite FTS
   - Human-gated AI workflows
   - Open hardware and open-source collaboration

3. How it works
   - Ingest evidence
   - Hash and index it
   - Query locally
   - Generate bounded proposals
   - Review and publish through GitHub

4. Feature grid
   - Knowledge pods
   - Provenance receipts
   - Local models
   - Retrieval adapters
   - Evidence browser
   - Git-native collaboration

5. Open-source section
   - GitHub repository link
   - Contribution guide link
   - Issue tracker link
   - License and community links

6. Footer
   - OpenRoot name
   - GitHub
   - Docs
   - License
   - “Built for local-first, verifiable collaboration.”

## Application layout requirements

Create a consistent application shell:

- Left sidebar navigation
- Top bar with project/search/status controls
- Main content area
- Status or provenance panel where appropriate
- Responsive layout for desktop and mobile
- Accessible color contrast and keyboard navigation

Navigation items:
- Dashboard
- Knowledge Pods
- Evidence Browser
- Search
- Provenance
- Tasks
- GitHub

## Visual direction

- Dark-first interface with a light-mode fallback
- Clean neutral background
- One strong accent color
- Rounded cards and subtle borders
- Monospace styling for hashes, paths, and technical values
- No heavy JavaScript frameworks unless already present in the project
- Prefer semantic HTML, modern CSS, and progressive enhancement

## Hard boundaries

- Do not expose secrets, tokens, private repository data, or absolute local paths.
- Do not add autonomous commit, push, PR, deletion, spending, or remote-execution features.
- Keep all AI/model actions human-gated.
- Preserve existing OpenLoom evidence and provenance behavior.
- Do not break existing tests or CLI entry points.
- Use accessible, semantic HTML.
- Keep dependencies minimal.

## Deliverables

- Updated homepage/landing page
- Shared application layout/navigation shell
- Updated CSS/design tokens
- Dashboard view
- Evidence browser integration or placeholder route
- Search interface or placeholder route
- Provenance panel or placeholder route
- Updated README with screenshots or usage instructions
- Tests for routes, layout rendering, and core interactions

## Acceptance gate

- Existing tests pass.
- New tests pass.
- Application starts locally.
- Homepage renders correctly.
- Navigation works across main views.
- No secrets or absolute personal paths are committed.
- `openloom verify --pod demo-pod` returns `"passed": true`.

Stop after implementing and testing v1. Do not commit, push, or open a PR.

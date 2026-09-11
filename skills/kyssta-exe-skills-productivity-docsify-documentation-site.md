---
name: docsify-documentation-site
description: Create a docsify-based GitHub Pages documentation site with a full hierarchy of pages, cross-referenced against source code, plus root-level README, CONTRIBUTING, and LICENSE files.
---

# Creating a Docsify Documentation Site

Trigger: User asks to "create GitHub Pages docsify documentation site" or "create documentation site" for an existing project.

## Workflow

### 1. Analyze the Project First

Before writing a single doc file, exhaustively read the source code:

- **Build files**: `build.gradle.kts`, `package.json`, `Cargo.toml`, etc. (project metadata, version, dependencies)
- **Plugin metadata**: `plugin.yml`, `mod.yml`, `fabric.mod.json` (commands, permissions, entrypoints)
- **Configuration files**: default configs in resources (all settings, their defaults, and descriptions)
- **Core source files**: main entry point, API classes, interfaces, enums, models — these define the developer-facing surface
- **Utility classes**: web servers, webhook managers, storage backends
- **Data schemas**: JSON examples, SQL table definitions
- **Existing documentation** (if any): avoid gaps/duplication

### 2. Create Docsify Infrastructure

The entry point is `docs/index.html` with:

```html
<!-- Essential docsify configuration -->
window.$docsify = {
  name: '<span>Brand</span>Name',     // rendered logo/title
  repo: 'https://github.com/user/repo',  // GitHub corner link
  basePath: '/RepoName/',             // GitHub Pages subpath
  loadSidebar: true,                  // _sidebar.md nav
  coverpage: true,                    // _coverpage.md landing
  auto2top: true,
  maxLevel: 4,
  search: { placeholder: 'Search...' },
  plugins: [
    // Custom plugin for badge replacement, etc.
  ]
};
```

**Theming guidelines:**
- Match the project's brand colors (primary accent + highlight)
- Use the dark docsify theme for modern projects
- Override CSS variables for sidebar, headings, code blocks, tables
- Include plugins: `search`, `copy-code`, optional `toc`
- Use a custom `docsify-plugin` for badge macros (e.g., `[BADGE_PAPER]` → HTML badges)

### 3. Create Sidebar Navigation (_sidebar.md)

Organize content in tiered categories:

```
- **Getting Started**
  - [Overview](README.md)
  - [Installation](installation.md)
- **Core Features**
  - [Commands](commands.md)
  - [Permissions](permissions.md)
  - [Configuration](configuration.md)
- **Advanced**
  - [Storage](storage.md)
  - [Webhooks](webhooks.md)
  - [Developer API](api.md)
- **Operations**
  - [Import](import.md)
  - [FAQ](faq.md)
```

Keep sidebar concise — each link maps to a real `.md` file.

### 4. Write Documentation Pages

**Coverpage (`_coverpage.md`)** — single-page landing with gradient title, tagline, and action buttons linking to docs and GitHub.

**Installation (`installation.md`):**
- Requirements (versions, dependencies)
- Download/install steps
- Building from source (if applicable)
- Quick start / first-use walkthrough
- Update procedure

**Commands (`commands.md`):**
- Flags table first (shared flags like `-s`, `-p`)
- Organized by category (punishment, removal, investigation, staff tools, admin)
- Each command: H3 heading, usage, aliases, permission, 1-2 examples
- Extract ALL commands from the source code's command registry/plugin.yml

**Permissions (`permissions.md`):**
- Organized by category matching commands structure
- Permission node, description, defaults
- MUST verify every permission node from source code is documented (parse `plugin.yml` or equivalent)

**Configuration (`configuration.md`):**
- Document every config section with its YAML block and explanation
- Include messages.yml (placeholders, format)
- Include template/ladder system details

**Advanced pages (storage, webhooks, web-interface, API, import):**
- Storage: drivers, connection pooling, auto-downloaded drivers, cross-server sync
- Webhooks: URLs, embed format, event types
- Web Interface: dashboard routes, REST API endpoints with request/response examples
- Developer API: how to get the instance, key classes, complete method signatures, model docs, enums
- Import: supported sources, CLI syntax, JSON format reference

### 4a. GitHub Actions CI/CD Setup

Every docsify documentation site needs two GitHub Actions workflows for automated publishing:

**1. Modrinth/GitHub Release CI (`build.yml`)**
```yaml
name: Build & Publish
on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: 21
          distribution: temurin
      - name: Build with Gradle
        run: ./gradlew shadowJar
      - name: Upload JAR artifact
        uses: actions/upload-artifact@v4
        with:
          name: PluginName
          path: build/libs/PluginName-*.jar

  publish-modrinth:
    if: github.event_name == 'release'
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: 21
          distribution: temurin
      - run: ./gradlew shadowJar
      - uses: Kir-Antipov/mc-publish@v3.3
        with:
          modrinth-id: your-project-id      # ⚠️ Get from Modrinth project settings
          modrinth-token: ${{ secrets.MODRINTH_TOKEN }}
          files: build/libs/PluginName-*.jar
          name: PluginName ${{ github.ref_name }}
          version: ${{ github.ref_name }}
          game-versions: 1.21, 1.21.1, 1.21.3, 1.21.4, 26.0, 26.1
          loaders: paper, purpur
          java: 21
```

**Pitfall:** `Kir-Antipov/mc-publish@v3.3` — do NOT use v3.4 or higher, they don't exist. Verify the latest on the GitHub Marketplace before picking a version.

**2. GitHub Pages Deploy (`docs.yml`)**
```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'README.md'

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

**Critical setup:** The user MUST go to repo **Settings → Pages → Source: GitHub Actions** and select it. If Pages is set to "Deploy from a branch" (the default), the `configure-pages@v4` step fails with `HttpError: Not Found`. This is the #1 cause of docs deploy failures — the workflow is correct but Pages isn't enabled for Actions.

**Automatic trigger note:** The docs workflow only triggers when files under `docs/` change. If only the README changes (which is listed as a trigger path too), it also deploys. For initial setup after enabling Pages, you may need to push a trivial change to a docs file to kick off the first deploy.

### 4b. GitHub Pages Configuration

The `index.html` must have `basePath` set to exactly the repository name (case-sensitive):

```js
window.$docsify = {
  name: '<span>Brand</span>Name',
  repo: 'https://github.com/user/repo',
  basePath: '/RepoName/',           // ← must match GitHub repo name
  loadSidebar: true,
  coverpage: true,
  auto2top: true,
  // ...
};
```

If the repo is `kyssta-exe/casualbans`, `basePath` must be `/casualbans/`. If the repo is `MyOrg/MyPlugin`, `basePath` must be `/MyPlugin/`. A mismatch causes all page links to 404.

### 4c. Multi-Location URL Verification

When a project's GitHub username or repo name changes (e.g. `Kyssta/CasualBans` → `kyssta-exe/casualbans`), documentation links exist in MANY locations. Run a search-and-replace across:

- `docs/index.html` — repo link, favicon URL, `basePath`
- `docs/_coverpage.md` — GitHub link
- `docs/README.md` — links to issues, releases
- `docs/faq.md` — links to issues, contributing
- `docs/installation.md` — download URL
- `CONTRIBUTING.md` — new issue link
- `README.md` — badges (repository name), clone URL, issues link
- `.github/workflows/build.yml` — changelog URL in badge
- Any `.md` file with `github.com/user/repo` mentions

Use a batch search:
```bash
grep -r "old-user/old-repo" --include="*.md" --include="*.yml" --include="*.html" .
```

### 5. Create Root Files

All must be internally consistent with each other AND with the docs:

- **`README.md`** — badges, feature list, quick start, commands table, permissions overview, config snippet, build instructions, documentation links. Keep this as the project's GitHub landing page.
- **`CONTRIBUTING.md`** — PR process, build steps, code style, commit convention (Conventional Commits), bug reporting, feature requests
- **`LICENSE`** — MIT (most common for Minecraft plugins), Apache 2.0, GPL, etc.

### 6. Cross-Verify Documentation Against Source

This is the critical step that catches omissions. Write an ad-hoc verification script that:

- Checks every required file exists
- Parses `plugin.yml` (or equivalent) for command names → verifies each is documented in commands.md
- Parses `plugin.yml` for permission nodes → verifies each is documented in permissions.md
- Checks sidebar links resolve to actual files
- Validates HTML structure (docsify scripts, config)
- Verifies README badges, sections, and examples
- Checks CONTRIBUTING has key sections
- Verifies file sizes are non-trivial

Example pattern (bash):

```bash
# Verify every permission from source is in docs
grep -E '^  casualbans\.' plugin.yml | sed 's/:.*//' | while read perm; do
    grep -qiF "$perm" docs/permissions.md || echo "MISSING: $perm"
done
```

## Pitfalls

- **Don't write docs from memory** — always read the actual source files first. Documentation that doesn't match code is worse than no documentation.
- **Don't assume command names** — extract them from the actual command registry or plugin.yml, not from your knowledge.
- **Don't stop at writing files** — run a verification check that cross-references docs against source.
- **Don't forget the docsify basePath** — it must match the GitHub repo name exactly for Pages to serve correctly at `https://user.github.io/RepoName/`.
- **Permissions and commands drift** — if source changes, re-run verification. The docs and source must always match.
- **File overwrites from parallel tooling** — when creating many files in one turn, sibling writes can overwrite each other. Read before write if there's any chance of a conflict.
- **GitHub Pages must be set to "GitHub Actions"** — the `Deploy Docs` workflow fails with `HttpError: Not Found` in the `configure-pages@v4` step if the repo's Pages source isn't set to GitHub Actions. The user must go to Settings → Pages → Source → pick "GitHub Actions". This is the #1 cause of docs deploy failures and the error message is cryptic.
- **Username/repo changes break all links** — when the project moves orgs, every `.md` and `.yml` file referencing `github.com/old-org/repo` must be updated. Run a batch grep across all docs and root files before declaring done.
- **mc-publish action versioning** — `Kir-Antipov/mc-publish@v3.4` does NOT exist. Use `v3.3` which is the latest. Always verify action versions on the GitHub Marketplace before hardcoding.
- **Docs workflow only fires on docs/ changes** — the `paths:` filter means pushing to `src/` won't deploy docs. For the first deployment after enabling Pages, push a trivial change to a docs file (or re-run the workflow manually).

## Verification

After creating all files, run an ad-hoc verification script (see step 6) and fix all real failures before declaring done. False positives from the script's parsing logic should be distinguished from real missing content.

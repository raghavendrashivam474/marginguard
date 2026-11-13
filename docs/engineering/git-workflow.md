
# Git Workflow

**Project:** MarginGuard
**Sprint:** MG-S0.1
**Last Updated:** 2025-07-11

---

## Branch Naming

All branches follow the pattern:

```
<type>/<sprint-id>-<short-description>
```

### Branch types

| Type | Purpose | Example |
|------|---------|---------|
| `feature/` | New functionality or sprint work | `feature/MG-S0.1-project-foundation` |
| `fix/` | Bug fixes | `fix/MG-S0.2-health-endpoint-timeout` |
| `docs/` | Documentation-only changes | `docs/MG-S0.2-api-contracts` |
| `refactor/` | Code restructuring (no behaviour change) | `refactor/MG-S0.3-domain-models` |
| `chore/` | Maintenance, dependencies, config | `chore/MG-S0.2-upgrade-fastapi` |
| `hotfix/` | Urgent production fixes | `hotfix/MG-S1.0-auth-bypass` |

### Rules

- Use lowercase and hyphens only.
- Always include the sprint ID when applicable.
- Keep descriptions short but descriptive.
- Do not use spaces or underscores.

---

## Commit Naming

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>
```

### Commit types

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `chore` | Build, config, dependencies |
| `ci` | CI/CD pipeline changes |

### Scope (optional)

Use the application or module affected:

- `web` — Frontend
- `api` — Backend
- `contracts` — Shared schemas
- `infra` — Infrastructure / Docker

### Examples

```
chore: initialize repository foundation
chore: establish application directory structure
chore(web): initialize frontend application
chore(api): initialize backend application
feat(api): add health check endpoints
docs: add development setup instructions
docs: add repository inspection report
test(api): verify application health endpoints
fix(web): resolve Tailwind path alias configuration
```

### Rules

- Use imperative mood ("add" not "added" or "adds").
- Do not capitalize the first letter.
- Do not end with a period.
- Keep the first line under 72 characters.
- Add a blank line before any extended description.

---

## Pull Request Expectations

### Before opening a PR

1. Ensure your branch is up to date with `main`.
2. Run all relevant tests locally.
3. Verify both applications start successfully.
4. Review your own diff (`git diff main...HEAD`).
5. Remove any debug code, commented-out blocks or temporary files.

### PR title format

Use the same Conventional Commits format:

```
feat(api): implement invoice ingestion pipeline
```

### PR description template

```markdown
## Summary
Brief description of what this PR does.

## Sprint
MG-SX.X — Sprint Name

## Changes
- List of key changes

## Testing
- How to verify the changes

## Checklist
- [ ] Tests pass locally
- [ ] Both applications start successfully
- [ ] No secrets or sensitive data committed
- [ ] Documentation updated if applicable
- [ ] No unrelated changes included
```

### Review expectations

- At least one approval required before merging.
- All CI checks must pass.
- Resolve all review comments before merging.
- Do not merge your own PR without review (except for solo development phases).

---

## Merge Rules

### Strategy

- Use **squash and merge** for feature branches to keep `main` history clean.
- Use **rebase and merge** for long-lived branches that need to preserve individual commits.
- Do not use merge commits for feature branches.

### Protected branches

| Branch | Protection |
|--------|-----------|
| `main` | Require PR, require review, require passing checks |
| `develop` | (future) Same as main when team grows |

### After merging

1. Delete the feature branch.
2. Update your local `main`: `git switch main && git pull`.
3. Close or update related sprint tasks.

---

## Workflow Summary

```
1. git switch main
2. git pull
3. git switch -c feature/MG-SX.X-description
4. ... work, commit in small increments ...
5. git push -u origin feature/MG-SX.X-description
6. Open PR → review → squash merge
7. git switch main && git pull
8. git branch -d feature/MG-SX.X-description
```

---

## Sprint MG-S0.1 Branch

The foundation sprint uses:

```
feature/MG-S0.1-project-foundation
```

All work in this sprint is committed to this branch and merged to `main` upon sprint completion.
```

---
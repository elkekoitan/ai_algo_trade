# Contributing Guidelines

First off, thank you for considering contributing to **ICT Ultra Platform**! Following these guidelines helps maintain consistency and quality.

---

## 1. Code of Conduct

We follow the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) – be respectful.

---

## 2. Getting Started

1. Fork the repo & create your feature branch:  
   `git checkout -b feat/signal-optimizer`
2. Ensure you can run the tests (`pytest`, `pnpm test`).
3. Write or update docs for any behavior change.

---

## 3. Commit Messages

Use **Conventional Commits**:

```
feat(signals): add divergence detector
fix(risk): correct max_drawdown calculation
chore(deps): bump axios 1.10 → 1.11
```

---

## 4. Pull Request Checklist

- [ ] Tests pass & coverage ≥ 90 %.
- [ ] `pnpm run lint` & `ruff .` show no errors.
- [ ] Docs updated (`docs/`, Swagger, Storybook).
- [ ] Linked to issue (e.g., `Fixes #123`).

PRs are reviewed within **48 hours**.

---

## 5. Signing Your Work (DCO)

All commits must be signed to certify you wrote the code:

```bash
git commit -s -m "feat: awesome change"
```

---

## 6. Issue Triage Labels

| Label | Meaning |
|-------|---------|
| `bug` | Unexpected behavior |
| `enhancement` | New feature or improvement |
| `documentation` | Docs-only change |
| `good first issue` | Safe for new contributors |

---

Thank you for helping make ICT Ultra Platform better! 🚀 
#!/bin/bash
set -e

echo "🌱 OpenRoot Community Files → GitHub"
echo "===================================="
echo ""

cd ~/openroot || exit 1

echo "📋 Creating community files..."

cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Covenant Code of Conduct

## Our Commitment

We are committed to providing a welcoming and inspiring community for all. We pledge that everyone participating in the OpenRoot community and its projects will be treated with respect and dignity.

## Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing opinions, viewpoints, and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- Harassment of any kind
- Trolling, insulting, or derogatory comments
- Personal or political attacks
- Publishing others' private information without permission
- Discriminatory behavior

## Enforcement

Report issues to: jrm8908@proton.me

---

Adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.0.
EOF

cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly.

**Do not open a public GitHub issue** for security vulnerabilities.

Instead, email: **jrm8908@proton.me**

Include:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Your contact information

## Response Timeline

We aim to:
1. Acknowledge receipt within 48 hours
2. Investigate and provide an initial response within 7 days
3. Release a fix or mitigation as soon as possible

## Hardware Safety

For physical hardware designs:
- Review designs for unintended hazards before building
- Test in controlled environments first
- Report discovered safety issues via security email
- Do not publicly disclose safety issues until a fix is available

Thank you for helping keep OpenRoot safe.
EOF

mkdir -p .github/ISSUE_TEMPLATE

cat > .github/pull_request_template.md << 'EOF'
# Pull Request

## What does this PR do?

Brief description of the changes.

## Related Issue

Closes #(issue number) or references #(issue number)

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Design improvement
- [ ] Thermal loop validation
- [ ] ACRE token work

## How to Validate This

Steps to test or verify:

1. 
2. 

## Checklist

- [ ] I've tested this locally
- [ ] I've updated relevant documentation
- [ ] I've followed the hard rules (no patents, no >100% efficiency claims, etc.)
- [ ] I've documented any failures honestly

---

Thank you for contributing to OpenRoot. 🌱
EOF

cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
# Bug Report

## Description

Brief description of the bug.

## Steps to Reproduce

1. 
2. 
3. 

## Expected Behavior

What should happen.

## Actual Behavior

What actually happened.

## Environment

- **Location/Node:** 
- **OS:** 
- **Relevant Software:** 

---

**Is this a safety issue?** Email jrm8908@proton.me instead of posting publicly.
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
# Feature Request

## Description

What feature would you like to see?

## Problem It Solves

Why is this needed?

## Proposed Solution

How should this work?

## Additional Context

- Related designs/projects: 
- Priority level: (nice-to-have / important / blocking)
- Affects: (hardware / software / token / documentation)

---

**Have a design ready?** Attach sketches, CAD files, or code samples.

**Want to build this?** Comment below and we'll discuss bounty eligibility!
EOF

cat > .github/ISSUE_TEMPLATE/validator_application.md << 'EOF'
# Validator Application

## Location

Where are you based?

## Experience

What's your background with:
- Hardware validation?
- Thermal measurement?
- Open source?
- Other relevant skills?

## What You'll Validate

Which part of OpenRoot interests you?
- [ ] Thermal loop nodes
- [ ] Water systems
- [ ] ACRE token mechanics
- [ ] Mesh networking
- [ ] Hardware fabrication
- [ ] Other: ___________

## How You'll Participate

How often can you validate?
- [ ] Weekly
- [ ] Monthly
- [ ] As-needed

## Contact

- Email: 
- GitHub: 
- Location timezone: 

---

Validators earn ACRE for each verified build. False approvals cost reputation.

Thank you for stepping up. 🌱
EOF

echo "✅ Files created"
echo ""

echo "📦 Staging files..."
git add CODE_OF_CONDUCT.md SECURITY.md .github/

git status

echo ""
read -p "Ready to commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Add: CODE_OF_CONDUCT, SECURITY, PR template, and issue templates"
    echo "✅ Committed"
else
    echo "⏭️  Skipped"
    exit 0
fi

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Done! Community files are now live."
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/jesseray718/openroot"
echo "2. Settings → Features → Enable 'Discussions'"
echo "3. Create your first 'Help Wanted' issue"
echo ""
echo "Warriors of the Rainbow 🌱"

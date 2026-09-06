# OpenRoot Ecosystem Git Push Guide

## Current Status
All repositories are up to date with their remote branches.

## Repository List
- OpenCell-Thermal-System ✅
- aerocement ✅
- agape-une ✅
- civilization2.0 ✅
- jesseray718 ✅
- openroot ✅
- openroot-spoke-template ✅

## Push All Repositories
```bash
cd ~/openroot-ecosystem
./push_all.sh
```

## Individual Push Commands
```bash
# OpenCell-Thermal-System
cd ~/openroot-ecosystem/OpenCell-Thermal-System
git push origin main

# aerocement
cd ~/openroot-ecosystem/aerocement
git push origin main

# agape-une
cd ~/openroot-ecosystem/agape-une
git push origin main

# civilization2.0
cd ~/openroot-ecosystem/civilization2.0
git push origin main

# jesseray718
cd ~/openroot-ecosystem/jesseray718
git push origin main

# openroot
cd ~/openroot-ecosystem/openroot
git push origin main

# openroot-spoke-template
cd ~/openroot-ecosystem/openroot-spoke-template
git push origin main
```

## Troubleshooting

### If you get "repository archived" error:
```bash
git config --unset remote.origin.archive
```

### If you need to unarchive a repository:
1. Go to GitHub repository settings
2. Scroll to "Archive this repo"
3. Click "Unarchive this repository"

### Force push (use with caution):
```bash
git push --force origin main
```

## Best Practices
- Always pull before pushing: `git pull origin main`
- Check status first: `git status`
- Commit changes: `git add . && git commit -m "message"`
- Push: `git push origin main`

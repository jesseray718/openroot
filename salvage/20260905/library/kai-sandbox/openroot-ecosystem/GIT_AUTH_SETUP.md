# GitHub Authentication Setup

## One-time credential setup

Since you're using HTTPS remotes, Git needs your GitHub credentials. Here's how to set it up:

1. Run this command to cache your credentials:
   ```bash
   git config --global credential.helper store
   ```

2. Manually push one repository to trigger credential prompt:
   ```bash
   cd ~/openroot-ecosystem/OpenCell-Thermal-System
   git push origin main
   ```

3. When prompted, enter:
   - Username: jesseray718
   - Password: [your GitHub personal access token or password]

4. Your credentials will be stored in ~/.git-credentials

## Alternative: Switch to SSH (recommended)

1. Change remote URLs to SSH:
   ```bash
   cd ~/openroot-ecosystem
   ./switch_to_ssh.sh
   ```

2. Set up SSH keys on your computer

## After authentication is set up

Run the push script:
```bash
cd ~/openroot-ecosystem
bash push_all.sh
```

# SSH Setup Guide for GitHub

## Step 1: Generate SSH Key (on your computer)

```bash
ssh-keygen -t ed25519 -C "jesse@openroot.earth"
```

Press Enter to accept default file location
Enter a secure passphrase (or leave empty)

## Step 2: Add SSH Key to SSH Agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

## Step 3: Add SSH Key to GitHub

1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub | pbcopy  # Mac
   cat ~/.ssh/id_ed25519.pub | xclip    # Linux
   ```

2. Go to GitHub → Settings → SSH and GPG keys
3. Click "New SSH key"
4. Paste your public key
5. Title: "OpenRoot Ecosystem"
6. Click "Add SSH key"

## Step 4: Test SSH Connection

```bash
ssh -T git@github.com
```

You should see: "Hi jesseray718! You've successfully authenticated..."

## Step 5: Push All Repositories

```bash
cd ~/openroot-ecosystem
bash push_all.sh
```

## Troubleshooting

If you get permission denied:
- Make sure SSH agent is running: `eval "$(ssh-agent -s)"`
- Add your key: `ssh-add ~/.ssh/id_ed25519`
- Test connection: `ssh -T git@github.com`

If you get "repository not found":
- Double-check repository names on GitHub
- Make sure you have access to all repositories

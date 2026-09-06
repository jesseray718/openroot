# GitHub SSH Setup - Complete Guide

## Your SSH Key

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIErAoiUPwBQbBaIYyzMHjuVjQEor29TMYhV6iglEQ0Cj jesse@openroot.earth
```

## Step 1: Add Key to GitHub

1. Copy the entire key above (starts with `ssh-ed25519`)
2. Go to GitHub.com → Settings → SSH and GPG keys
3. Click "New SSH key"
4. Title: "Termux OpenRoot"
5. Paste your key
6. Click "Add SSH key"

## Step 2: Test SSH Connection

```bash
ssh -T git@github.com
```

You should see: "Hi jesseray718! You've successfully authenticated..."

## Step 3: Push All Repositories

```bash
cd ~/openroot-ecosystem
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/termux_id_ed25519
bash push_all.sh
```

## Troubleshooting

If you get errors:
- Make sure the key is added: `ssh-add -l`
- Check SSH agent: `eval "$(ssh-agent -s)"`
- Test connection: `ssh -T git@github.com`

## Key Files

- Private key: `~/.ssh/termux_id_ed25519` (keep this secret!)
- Public key: `~/.ssh/termux_id_ed25519.pub` (share this with GitHub)

## Success!

Once SSH is working, all your repositories will push smoothly with:
```bash
cd ~/openroot-ecosystem && bash push_all.sh
```

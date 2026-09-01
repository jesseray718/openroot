# Uplift Recovery Runbook
Generated: 2026-09-01T05:33:31Z

## What this fixed
1. Recreated missing:
   - shell/openroot.sh
   - shell/termux-hook.sh
2. Added session env fallback:
   - ~/.config/environment.d/99-openroot-session.conf
3. Attempted to suppress keyring autostart prompt loop.

## Verify
- Run: /home/jesse/openroot/shell/openroot.sh
- Run: /home/jesse/openroot/scripts_uplift_health.sh

## If keyring loop persists
- Reboot user session.
- Check: journalctl --user -b | grep -i keyring
- Optionally reinstall:
  sudo apt install --reinstall gnome-keyring seahorse

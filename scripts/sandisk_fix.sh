#!/bin/bash
set -eu
ssh -t jesse@100.122.169.43 'set -eu
FS=$(findmnt -n -o FSTYPE /mnt/sdb1)
echo "[sandisk] fstype: $FS"
case "$FS" in
  vfat|exfat|ntfs)
    U=$(id -u jesse); G=$(id -g jesse)
    sudo umount /mnt/sdb1
    sudo mount -t $FS -o uid=$U,gid=$G,umask=022 /dev/sdb1 /mnt/sdb1 ;;
  *) sudo chown -R jesse:jesse /mnt/sdb1/openroot ;;
esac
grep -q "^/dev/sdb1" /etc/fstab || {
  sudo cp /etc/fstab /etc/fstab.bak.$(date +%s)
  echo "/dev/sdb1 /mnt/sdb1 $FS defaults,uid=$(id -u jesse),gid=$(id -g jesse),umask=022,nofail,x-systemd.device-timeout=10 0 0" | sudo tee -a /etc/fstab >/dev/null
  echo "[fstab] entry added (backup taken)"
}
sudo -u jesse mkdir -p /mnt/sdb1/openroot/{cas,backups,salvage-archive,model-cache,exports}
sudo -u jesse touch /mnt/sdb1/openroot/.write-test && echo "[sandisk] WRITABLE as jesse"
echo "[✅ DONE] sandisk owned + fstab persisted"'

#!/data/data/com.termux/files/usr/bin/bash
set -u
mkdir -p /data/data/com.termux/files/home/openroot/workflow
mkdir -p /sdcard/openroot/context_bridge
exec >> /data/data/com.termux/files/home/openroot/workflow/push_fix.log
exec 2>&1
echo START
date -Iseconds

echo DIAG_COORD
if [ -d /data/data/com.termux/files/home/agape-coordination/.git ]
then
  git -C /data/data/com.termux/files/home/agape-coordination status -sb
  git -C /data/data/com.termux/files/home/agape-coordination rev-parse --abbrev-ref HEAD
  git -C /data/data/com.termux/files/home/agape-coordination remote -v
  git -C /data/data/com.termux/files/home/agape-coordination fetch origin
  git -C /data/data/com.termux/files/home/agape-coordination branch -vv
  git -C /data/data/com.termux/files/home/agape-coordination ls-remote --heads origin
  git -C /data/data/com.termux/files/home/agape-coordination log -1 --oneline
else
  echo NO_CLONE_COORD
fi

echo GH
gh auth status

echo FIX_COORD
if [ -d /data/data/com.termux/files/home/agape-coordination/.git ]
then
  git -C /data/data/com.termux/files/home/agape-coordination remote set-url origin https://github.com/jesseray718/agape-coordination.git
  loc=`git -C /data/data/com.termux/files/home/agape-coordination rev-parse --abbrev-ref HEAD`
  echo LOCAL
  echo "$loc"
  if git -C /data/data/com.termux/files/home/agape-coordination ls-remote --heads origin main | grep -q refs/heads/main
  then
    if [ "$loc" != main ]
    then
      git -C /data/data/com.termux/files/home/agape-coordination branch -M main
    fi
    git -C /data/data/com.termux/files/home/agape-coordination push -u origin main
  else
    git -C /data/data/com.termux/files/home/agape-coordination push -u origin "$loc"
  fi
fi

echo FINISH_LOOP
SKIP='firmware LXMF markor MeshCore Reticulum RNode_Firmware tinyGS skills-introduction-to-github civilization2.0 aerocement- open-cell-thermal-open-cell-the AeroCement_Ecosystem renaissance-protocol OpenCell-Thermal-System'
find /data/data/com.termux/files/home -maxdepth 2 -type d -name .git | sort | while read -r g
do
  repo=`dirname "$g"`
  name=`basename "$repo"`
  echo ----
  echo "$name"
  case " $SKIP " in
    *" $name "*)
      echo SKIP_FORK_OR_ARCHIVE
      continue
      ;;
  esac
  url=`git -C "$repo" remote get-url origin 2>/dev/null || true`
  if [ -z "$url" ]
  then
    echo NO_ORIGIN
    continue
  fi
  case "$url" in
    *github.com/jesseray718/*)
      ;;
    *)
      echo NOT_OURS
      echo "$url"
      continue
      ;;
  esac
  git -C "$repo" add -A
  git -C "$repo" reset -q -- '*.pem' '*.key' id_rsa id_ed25519 .ssh '*.gguf' '*.safetensors' || true
  if git -C "$repo" diff --cached --quiet
  then
    echo nothing_to_commit
  else
    git -C "$repo" commit -m 'stage: remaining local artifacts'
  fi
  br=`git -C "$repo" rev-parse --abbrev-ref HEAD`
  echo PUSH
  echo "$name"
  echo "$br"
  echo "$url"
  if git -C "$repo" push -u origin "$br"
  then
    echo OK
  else
    echo FAIL_FIRST
    if git -C "$repo" ls-remote --heads origin main | grep -q refs/heads/main
    then
      git -C "$repo" branch -M main
      if git -C "$repo" push -u origin main
      then
        echo OK_MAIN
      else
        echo FAIL_MAIN
      fi
    else
      echo STILL_FAIL
    fi
  fi
done

{
  echo STAGE_PUSH_FIX
  date -Iseconds
  echo HOME_REPOS
  find /data/data/com.termux/files/home -maxdepth 2 -type d -name .git | sort
  echo SD_TOP
  ls -la /sdcard/openroot
} > /sdcard/openroot/context_bridge/STAGE_PUSH_REPORT.txt

echo REPORT_PATH
echo /sdcard/openroot/context_bridge/STAGE_PUSH_REPORT.txt
echo LOG_PATH
echo /data/data/com.termux/files/home/openroot/workflow/push_fix.log
echo DONE
date -Iseconds

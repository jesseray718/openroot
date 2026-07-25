#!/data/data/com.termux/files/usr/bin/bash
echo "--- Checking Common F-Droid Packages ---"
for app in com.digibites.android.fdroid org.fdroid.fdroid org.mobilism.android apkmirror; do
    [ -f "/data/data/$app/shared_prefs/settings.xml" ] && echo "✓ $app (likely installed)" || echo "✗ $app"
done

echo ""
echo "--- Your Termux Environment Packages ---"
pkg list-installed | wc -l
echo "packages installed in Termux"

echo ""
echo "Full list:"
pkg list-installed | grep -v "^$" | sort

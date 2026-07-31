cd ~/openroot-staging
for zipfile in *.zip */*.zip; do
    if [ -f "$zipfile" ]; then
        echo "Unzipping: $zipfile"
        unzip -o "$zipfile"
    fi
done

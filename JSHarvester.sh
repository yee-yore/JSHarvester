#!/bin/zsh

if [ -z "$1" ]; then
    echo "Usage: $0 [domain]"
    echo "Example: $0 example.com"
    exit 1
fi
DOMAIN=$1

echo "[1/6] Extracting URLs from $DOMAIN ..."
urx $DOMAIN --silent --providers wayback,cc,otx,vt,urlscan -o urx.txt
urlfinder -d $DOMAIN -silent -all -o urlfinder.txt
waymore -i $DOMAIN -mode U -oU waymore.txt

echo "[2/6] Concating URLs ..."
cat urx.txt urlfinder.txt waymore.txt > url.txt
cat url.txt | uro | tee uniq_url.txt

echo "[3/6] Filtering out-of-scope URLs ..."
cat uniq_url.txt | grep "//$DOMAIN" | tee in_scope.txt

echo "[4/6] Matching JS files"  
cat in_scope.txt | grep -E '\.js' | grep -Ev '\.(json|jsp|jsonp)' | tee js.txt

echo "[5/6] Checking alive .js"
cat js.txt | httpx -mc 200 -silent -o js_active.txt

echo "[6/6] Downloading .js and removing duplicates"
cat js_active.txt > js_live.txt
mkdir -p js_files

typeset -A hash_urls

while read url; do
    filename=$(echo "$url" | sed 's/[^a-zA-Z0-9]/_/g')
    curl -s -L -o "js_files/$filename" "$url"
    
    if [ -f "js_files/$filename" ]; then
        
        md5=$(md5 -q "js_files/$filename")
        
        if [ -z "${hash_urls[$md5]}" ]; then
            hash_urls[$md5]="$url"
        fi
    else
        echo "[!] Failed: $url"
    fi
done < js_live.txt


echo "URL" > js_unique.txt
for url in "${(v)hash_urls}"; do
    echo "$url" >> js_unique.txt
done

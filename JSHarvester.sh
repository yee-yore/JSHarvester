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
rm url.txt urx.txt urlfinder.txt waymore.txt

echo "[3/6] Filtering out-of-scope URLs ..."
cat uniq_url.txt | grep "//$DOMAIN" | tee in_scope_url.txt
rm uniq_url.txt

echo "[4/6] Matching JS files"  
cat in_scope_url.txt | grep -E '\.js' | grep -Ev '\.(json|jsp|jsonp)' | tee js.txt

echo "[5/6] Checking alive .js"
cat js.txt | httpx -mc 200 -silent -o js_active.txt

echo "[6/6] Downloading .js and removing duplicates"
mkdir -p "$DOMAIN"

typeset -A hash_urls

while read url; do
  base_filename=$(basename "$url" | sed 's/[^a-zA-Z0-9\.]/_/g')
  
  filename="$base_filename"
  counter=1
  
  while [ -f "$DOMAIN/$filename" ]; do
    filename="${base_filename%.*}(${counter}).${base_filename##*.}"
    ((counter++))
  done
  
  curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" -o "$DOMAIN/$filename" "$url"
  
  if [ -f "$DOMAIN/$filename" ]; then
    md5=$(cat "$DOMAIN/$filename" | md5)
    if [ -z "${hash_urls[$md5]}" ]; then
      hash_urls[$md5]="$url"
    else
      rm "$DOMAIN/$filename"
    fi
  else
    echo "[!] Failed: $url"
  fi
done < js_active.txt

for url in "${(v)hash_urls}"; do
  printf "%s\n" "$url" >> js_unique.txt
done

import os
import subprocess
import argparse
import sys
import tempfile
import requests
from urllib.parse import urlparse

def execute_command(command):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False

def js_download(js_file, download_dir):
    if not os.path.exists(js_file):
        return False
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    with open(js_file, "r", encoding="utf-8") as f:
        js_urls = [line.strip() for line in f if line.strip()]
    
    success_count = 0

    for url in js_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            file_name = url.split("/")[-1]
            file_path = os.path.join(download_dir, file_name)
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            success_count += 1
        except requests.exceptions.RequestException:
            pass
    
    return success_count > 0

def collect_urls(domain, outfile):
    temp_dir = tempfile.mkdtemp()
    
    urlfinder_file = os.path.join(temp_dir, "urlfinder.txt")
    katana_file = os.path.join(temp_dir, "katana.txt")
    urls_file = os.path.join(temp_dir, "urls.txt")
    httpx_file = os.path.join(temp_dir, "httpx.txt")
    filtered_file = os.path.join(temp_dir, "filtered.txt")
    uro_file = os.path.join(temp_dir, "uro.txt")
    
    # Step 1: Run urlfinder
    command = f"urlfinder -d {domain} -silent -all -m js -f json,jsp -o {urlfinder_file}"
    if not execute_command(command):
        open(urlfinder_file, 'w').close()
    
    # Step 2: Run katana
    command = f"katana -u {domain} -silent -jc -jsl -em js -o {katana_file}"
    if not execute_command(command):
        open(katana_file, 'w').close()
    
    # Step 3: Merge URLs with anew
    files_exist = all(os.path.exists(file) for file in [urlfinder_file, katana_file])
    if not files_exist:
        return False
    
    urlfinder_empty = os.path.getsize(urlfinder_file) == 0
    katana_empty = os.path.getsize(katana_file) == 0
    
    if urlfinder_empty and katana_empty:
        return False
    
    # Initialize with urlfinder
    if not urlfinder_empty:
        command_init = f"cat {urlfinder_file} > {urls_file}"
        execute_command(command_init)
    else:
        open(urls_file, 'w').close()
    
    # Merge katana
    if not katana_empty:
        try:
            command_anew = f"cat {katana_file} | anew {urls_file} > /dev/null"
            execute_command(command_anew)
        except:
            temp_file = f"{urls_file}.temp"
            execute_command(f"cat {urls_file} {katana_file} | sort | uniq > {temp_file}")
            execute_command(f"mv {temp_file} {urls_file}")
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            url_count = sum(1 for _ in f)
        if url_count == 0:
            return False
    except UnicodeDecodeError:
        return False
    
    # Step 4: Filter active URLs with httpx
    if not os.path.exists(urls_file):
        return False
    
    command = f"cat {urls_file} | httpx -silent -mc 200 -o {httpx_file}"
    execute_command(command)
    
    # Step 5: Filter JavaScript extensions
    if not os.path.exists(httpx_file):
        return False
    
    valid_extensions = ['.js']
    filtered_urls = []
    
    with open(httpx_file, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            parsed = urlparse(url)
            _, ext = os.path.splitext(parsed.path)
            if ext.lower() in valid_extensions:
                filtered_urls.append(url)
    
    with open(filtered_file, 'w', encoding='utf-8') as out:
        for url in filtered_urls:
            out.write(url + '\n')
    
    if len(filtered_urls) == 0:
        return False
    
    # Step 6: Run uro to optimize URLs
    if not os.path.exists(filtered_file):
        return False
    
    command = f"cat {filtered_file} | uro > {uro_file}"
    if not execute_command(command):
        execute_command(f"cp {filtered_file} {uro_file}")
    
    # Step 7: Process JS files - filter out external libraries
    if not os.path.exists(uro_file):
        return False
    
    external_libraries = [
        'jquery', 'bootstrap', 'react', 'vue', 'angular', 
        'lodash', 'underscore', 'moment', 'axios', 'ramda',
        'material-ui', 'tailwind', 'foundation', 'bulma', 'semantic',
        'd3', 'chart.js', 'highcharts', 'three.js', 'plotly',
        'gsap', 'anime', 'velocity', 'formik', 'redux',
        'mobx', 'zustand', 'recoil', 'jest', 'mocha',
        'chai', 'enzyme', 'cypress', 'socket.io', 'hammer',
        'popper', 'marked', 'pdf.js', 'quill', 'tinymce',
        'ckeditor', 'dayjs', 'swiper', 'fullpage', 'slick',
        'jindo', 'jplayer', 'swfobject', 'lottie', 'odometer',
        'skrollr', 'easing', 'cookie'
    ]
    
    try:
        with open(uro_file, 'r', encoding='utf-8') as f:
            js_urls = f.readlines()
        
        filtered_urls = []
        for url in js_urls:
            url = url.strip()
            if not url:
                continue
            
            filename = url.split('/')[-1].lower()
            
            is_external_lib = False
            for lib in external_libraries:
                if lib.lower() in filename:
                    is_external_lib = True
                    break
            
            if not is_external_lib:
                filtered_urls.append(url)
        
        # Create output directory if needed
        output_dir = os.path.dirname(outfile)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save final result
        with open(outfile, 'w', encoding='utf-8') as f:
            for url in filtered_urls:
                f.write(f"{url}\n")
        
        return len(filtered_urls) > 0
        
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="jsharvester - Collect JavaScript URLs from a domain")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. tesla.com)")
    parser.add_argument("-o", "--output", help="Output file path (default: {domain}_js.txt)")
    parser.add_argument("-jd", "--download", action="store_true", help="Download JavaScript files")
    
    args = parser.parse_args()
    
    try:
        outfile = args.output
        if not outfile:
            outfile = f"{args.domain}_js.txt"
        
        success = collect_urls(
            args.domain, 
            outfile=outfile
        )
        
        if not success:
            print(f"No JavaScript URLs found for {args.domain}")
            return 1
        
        if args.download:
            download_dir = args.domain
            download_success = js_download(outfile, download_dir)
            if download_success:
                print(f"JavaScript URLs saved to: {outfile}")
                print(f"JavaScript files downloaded to: {download_dir}/")
                return 0
            else:
                print(f"JavaScript URLs saved to: {outfile}")
                print(f"Failed to download JavaScript files")
                return 1
        else:
            print(f"JavaScript URLs saved to: {outfile}")
            return 0
    except Exception:
        print(f"Error processing {args.domain}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
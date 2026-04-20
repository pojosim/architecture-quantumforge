# Скрипт парсинга всех url

import subprocess
import time

with open('urls.txt') as f:
    for line in f:
        url, out = line.strip().split()
        subprocess.run(['python', 'fetch_clean_text.py', '--url', url, '--output', out])
        time.sleep(1)
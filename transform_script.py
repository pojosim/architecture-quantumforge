# Скрипт замены ключевых терминов на основе terms_map.json

import json
import re
from pathlib import Path

def apply_replacements(text, term_map):
    # Сортируем ключи по убыванию длины, чтобы избежать частичных замен
    for original, fake in sorted(term_map.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(original) + r'\b'
        text = re.sub(pattern, fake, text, flags=re.IGNORECASE)
    return text

def main():
    with open('terms_map.json', 'r', encoding='utf-8') as f:
        term_map = json.load(f)

    input_dir = Path('raw_texts')
    output_dir = Path('knowledge_base')
    output_dir.mkdir(exist_ok=True)

    for input_file in input_dir.glob('*.txt'):
        with open(input_file, 'r', encoding='utf-8') as f:
            original_text = f.read()
        transformed_text = apply_replacements(original_text, term_map)
        output_file = output_dir / input_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transformed_text)
        print(f"Processed {input_file.name}")

if __name__ == '__main__':
    main()
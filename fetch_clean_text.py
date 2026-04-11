import argparse
import re
import sys
from urllib.parse import urlparse, unquote
import mwclient

def extract_page_title_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path

    if not path.startswith('/wiki/'):
        raise ValueError(f"URL не содержит '/wiki/': {url}")
    title = path[6:]  # удаляем '/wiki/'
    # Декодируем URL-кодированные символы (например, %20 -> пробел)
    title = unquote(title)
    # Заменяем подчёркивания на пробелы (MediaWiki хранит с подчёркиваниями, но нам удобнее с пробелами)
    title = title.replace('_', ' ')
    return title

def clean_wikitext(wikitext: str) -> str:
    # Удаляем многострочные комментарии
    text = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)

    # Преобразуем внутренние ссылки с альтернативным текстом: [[target|text]] -> text
    text = re.sub(r'\[\[[^\]|]*\|([^\]]+)\]\]', r'\1', text)
    # Преобразуем простые внутренние ссылки: [[target]] -> target
    text = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', text)

    # Удаляем категории [[Category:...]] и другие служебные ссылки с префиксами
    text = re.sub(r'\[\[(?:Category|File|Image|Template|Help|Special):[^\]]+\]\]', '', text)

    # Удаляем внешние ссылки [http://example.com text] -> text (если есть)
    text = re.sub(r'\[https?://[^\s\]]+(?:\s+([^\]]+))?\]', lambda m: m.group(1) if m.group(1) else '', text)

    # Удаляем HTML-теги (включая <br>, <p> и т.д.)
    text = re.sub(r'<[^>]+>', '', text)

    # Удаляем шаблоны {{...}} (включая вложенные)
    # Простой способ: удаляем всё, что между {{ и }} с учётом вложенности — используем цикл
    prev_len = -1
    while len(text) != prev_len:
        prev_len = len(text)
        text = re.sub(r'\{\{[^{}]*\}\}', '', text)

    # Убираем множественные пустые строки, оставляя максимум одну пустую строку между абзацами
    lines = [line.strip() for line in text.splitlines()]
    # Удаляем пустые строки в начале и конце, а также подряд идущие пустые строки
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line == '':
            if not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    # Если последняя строка пустая, удаляем её
    if cleaned_lines and cleaned_lines[-1] == '':
        cleaned_lines.pop()

    return '\n'.join(cleaned_lines)

def fetch_page_text(wiki_domain: str, page_title: str) -> str:
    try:
        site = mwclient.Site(wiki_domain, path='/')
    except Exception as e:
        raise RuntimeError(f"Не удалось подключиться к {wiki_domain}: {e}")

    page = site.pages[page_title]
    if not page.exists:
        raise ValueError(f"Страница '{page_title}' не существует на {wiki_domain}")

    raw_text = page.text()
    if raw_text is None:
        raise ValueError(f"Не удалось получить содержимое страницы '{page_title}'")

    cleaned = clean_wikitext(raw_text)
    return cleaned

def main():
    parser = argparse.ArgumentParser(description="Скачивание и очистка текста со страницы через API")
    parser.add_argument('--url', '-u', required=True)
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()

    try:
        parsed_url = urlparse(args.url)
        domain = parsed_url.netloc
        if not domain:
            raise ValueError("Не удалось извлечь домен из URL")
        page_title = extract_page_title_from_url(args.url)
    except Exception as e:
        print(f"Ошибка при разборе URL: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Подключение к {domain}, загрузка страницы '{page_title}'...")
    try:
        content = fetch_page_text(domain, page_title)
    except Exception as e:
        print(f"Ошибка при загрузке: {e}", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        print("Предупреждение: полученный текст пуст или состоит только из пробелов.", file=sys.stderr)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Сохранено в {args.output} (размер {len(content)} символов)")
    except IOError as e:
        print(f"Ошибка записи файла: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
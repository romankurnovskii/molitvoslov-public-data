import os
import json
import glob

# --- НАСТРОЙКИ ---
INPUT_DIR = "data_input"  # Папка, где лежат новые JSON файлы
OUTPUT_DIR = "."  # Сохраняем прямо здесь (в корне репозитория)


def ensure_dir(path):
    """Создает папку, если её нет"""
    if not os.path.exists(path):
        os.makedirs(path)


def create_markdown(path, meta, content):
    """Создает .md файл с Frontmatter"""
    ensure_dir(os.path.dirname(path))

    yaml_lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        if isinstance(value, list):
            # Сохраняем русский текст как есть
            val_str = json.dumps(value, ensure_ascii=False)
            yaml_lines.append(f"{key}: {val_str}")
        elif isinstance(value, str):
            yaml_lines.append(f'{key}: "{value}"')
        else:
            yaml_lines.append(f"{key}: {value}")
    yaml_lines.append("---\n")
    yaml_lines.append(content)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines))
    print(f"✅ Создан/Обновлен: {path}")


def process_prayer_or_psalm(item):
    """Обработка одиночной молитвы или псалма"""
    slug = item.get("id")
    item_type = item.get("type", "prayer")

    # Определяем корневую папку (молитвы или псалтирь)
    root_folder = "молитвы"

    # Проверка: если это псалом или в категориях есть "Псалтирь"
    categories_lower = [c.lower() for c in item.get("categories", [])]
    if item_type == "psalm" or "псалтирь" in categories_lower:
        root_folder = "псалтирь"

    base_path = os.path.join(OUTPUT_DIR, root_folder, slug)

    meta = {
        "title": item.get("title"),
        "original_title": item.get("original_title"),
        "slug": slug,
        "categories": item.get("categories", []),
    }

    # 1. Русский файл
    if "content_ru" in item:
        create_markdown(os.path.join(base_path, "ru.md"), meta, item["content_ru"])

    # 2. Украинский файл (если есть)
    if "content_uk" in item:
        create_markdown(os.path.join(base_path, "uk.md"), meta, item["content_uk"])


def process_bible_book(data):
    """Обработка целой книги Библии"""
    testament = data.get("testament_slug", "other")
    book_slug = data.get("book_slug")
    book_title = data.get("book_title")
    common_cats = data.get("categories", [])

    base_book_path = os.path.join(OUTPUT_DIR, "библия", testament, book_slug)

    for chapter in data.get("chapters", []):
        chap_num = chapter["number"]
        # Форматируем номер главы: "глава-01"
        chap_slug = f"глава-{chap_num:02d}"

        meta = {"book": book_title, "chapter": chap_num, "categories": common_cats}

        chap_path = os.path.join(base_book_path, chap_slug)

        # Русский
        if "content_ru" in chapter:
            create_markdown(
                os.path.join(chap_path, "ru.md"), meta, chapter["content_ru"]
            )

        # Украинский
        if "content_uk" in chapter:
            create_markdown(
                os.path.join(chap_path, "uk.md"), meta, chapter["content_uk"]
            )


def main():
    print(f"🚀 Запуск скрипта. Ищу JSON в папке '{INPUT_DIR}'...")

    if not os.path.exists(INPUT_DIR):
        # Создаем папку для ввода, если её нет, чтобы пользователь не путался
        os.makedirs(INPUT_DIR)
        print(f"⚠️  Папка '{INPUT_DIR}' не была найдена, я создал её для вас.")
        print(
            f"👉 Положите ваши JSON файлы в папку '{INPUT_DIR}' и запустите скрипт снова."
        )
        return

    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))

    if not json_files:
        print(f"⚠️  В папке '{INPUT_DIR}' пусто. Добавьте .json файлы с молитвами.")
        return

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Если это список (массив)
            if isinstance(data, list):
                for item in data:
                    process_prayer_or_psalm(item)

            # Если это одиночный объект
            elif isinstance(data, dict):
                if data.get("type") == "bible_book":
                    process_bible_book(data)
                else:
                    process_prayer_or_psalm(data)

        except Exception as e:
            print(f"❌ Ошибка при чтении файла {file_path}: {e}")

    print("\n🎉 Готово! Данные обновлены в текущей папке.")


if __name__ == "__main__":
    main()

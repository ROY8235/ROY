import os
import re

def split_story_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # "Ch 1 -" जैसी हेडिंग पर चैप्टर काटना
    chapters = re.split(r'(Ch\s*\d+\s*-\s*.*)', content)

    if chapters[0].strip() == '':
        chapters = chapters[1:]

    combined_chapters = []
    for i in range(0, len(chapters), 2):
        title = chapters[i].strip()
        body = chapters[i + 1].strip() if i + 1 < len(chapters) else ""
        full_text = f"{title}\n\n{body}"
        filename = os.path.join("temp", f"chapter_{(i//2)+1}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_text)
        combined_chapters.append(filename)

    return combined_chapters

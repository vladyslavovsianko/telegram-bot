#!/usr/bin/env python3
"""
Запускать на сервере: python3 /opt/telegram-bot/update_group_ids.py
Обновляет group_chat_id в таблице clients на основе найденных диалогов.
"""
import sqlite3
import re

DB_FILE = '/opt/telegram-bot/bot_database.db'

# Результаты поиска из get_ids.py (tag_found → chat_id)
# "Lex 2" и "Lex 6" убраны — они ложно совпали с Lex 28 и Lex 69
FOUND = {
    "Lex 112": -5190574208,
    "Toy 77":  -5268591814,
    "Lex 106": -5000999147,
    "Toy 32":  -5207210520,
    "Lex 28":  -5269767297,
    "Toy 8":   -5143325351,
    "Toy 97":  -5113240025,
    "Lex 99":  -5223250049,
    "Toy 86":  -4913959792,
    "Toy 78":  -5101378007,
    "Lex 2":   -5257148446,
    "Lex 6":   -5112242325,
    "Lex 69":  -5170442208,
    "Lex 7":   -5279607641,
    "Lex 108": -5162609531,
    "Lex 102": -5292032613,
    "Lex 51":  -5102623265,
    "Lex 98":  -5194630033,
    "Lex 118": -5255514889,
    "#58":     -5227727762,
    "#136":    -5103239595,
    "#140":    -5102101973,
    "#140-2":  -5102101973,
    "#150":    -5297642350,
    "# 150":   -5297642350,
    "#154":    -5146314563,
    "# 154":   -5146314563,
    "#160":    -5130391065,
    "# 160":   -5130391065,
    "#1003":   -5166465730,
    "Lex 91":  -5111959825,
    "Lex 89":  -5258481777,
    "#46/47":  -5129896189,
    "Lex 70":  -5211761439,
    "#161":    -4875029494,
    "Toy 73":  -5021649061,
    "Lex 83":  -5193205713,
    "Lex 109": -5258708843,
    "Lex 103": -5072802527,
    "Lex 54":  -5120960431,
    "Toy 60":  -5298774186,
    "Toy 67":  -5234402500,
    "Toy 120": -5274079563,
    "Toy 110": -5199201964,
    "Lex 114": -5104582974,
    "Toy 88":  -5297076401,
    "Toy 38":  -5200145003,
    "Toy 82":  -5140398984,
    "Toy 113": -5245404630,
    "Toy 92":  -5244518625,
    "Toy 96":  -5234244146,
    "Lex 115": -5011743176,
    "Toy 95":  -5177844892,
    "Lex 117": -5286610120,
    "Toy 107": -5161226762,
    "Toy 85":  -5286642458,
    "Toy 93":  -5190558764,
    "Toy 94":  -5180383023,
    "Toy 104": -5216791737,
    "Toy 87":  -5241302367,
    "Toy 119": -5197663779,
    "Toy 105": -5156252498,
    "Toy 116": -5152111903,
    "Lex 111": -5219225522,
    "Toy 90":  -5276310174,
    "#152":    -5173362382,
    "#162":    -5021126555,
    "#155":    -5205193463,
    "#163":    -5264928587,
    "#156":    -5004997228,
    "#169":    -5189241130,
    "#168":    -5019503118,
    "#167":    -5162894077,
    "#166":    -5243878095,
    "#165":    -5236113769,
    "#164":    -5187316652,
    "#157":    -5110476146,
    "#159":    -5186626995,
    "#170":    -5070594070,
    "Toy 64":  -5174345325,
    "#114":    -4882418624,
    "#133":    -5125987879,
    "#144":    -5294989828,
    "#131":    -5291287861,
    "#142":    -5193651565,
    "#112":    -5162450800,
    "#127":    -5113224392,
    "#102":    -5141670241,
    "Toy 47":  -5249359726,
    "Toy 49":  -5267417206,
    "#139":    -5143478306,
    "#148":    -5247473724,
    "#124":    -5121925059,
    "Lex 19":  -5254977860,
    "Toy 44":  -5086915437,
    "Toy 30":  -5268553476,
    "Lex 72":  -5252922911,
    "#103":    -5233036184,
}

def normalize(s):
    """Убирает пробелы и приводит к нижнему регистру для сравнения."""
    return re.sub(r'\s+', '', s).lower()

# Переименования тегов: старый тег → (новый тег, правильный chat_id)
RENAMES = {
    "#70":    ("Lex 70",  -5211761439),
    "Lex 92": ("Toy 92",  -5244518625),
    "Lex113": ("Toy 113", -5245404630),
    "Lex 113":("Toy 113", -5245404630),
}

def main():
    conn = sqlite3.connect(DB_FILE)
    # Строим словарь: normalized_tag → chat_id
    norm_map = {normalize(k): v for k, v in FOUND.items()}

    # 1. Переименования + проставляем ID
    renamed = []
    for old_tag, (new_tag, gid) in RENAMES.items():
        rows = conn.execute(
            "SELECT id FROM clients WHERE client_tag=?", (old_tag,)
        ).fetchall()
        for (row_id,) in rows:
            conn.execute(
                "UPDATE clients SET client_tag=?, group_chat_id=? WHERE id=?",
                (new_tag, gid, row_id)
            )
            renamed.append(f"  {old_tag} -> {new_tag} (ID: {gid})")

    # 2. Обновляем group_chat_id для клиентов без него
    rows = conn.execute(
        "SELECT id, client_tag FROM clients WHERE is_active=1 AND (group_chat_id IS NULL OR group_chat_id=0)"
    ).fetchall()

    updated = []
    not_found = []

    for row_id, tag in rows:
        tag_norm = normalize(tag)
        if tag_norm in norm_map:
            gid = norm_map[tag_norm]
            conn.execute("UPDATE clients SET group_chat_id=? WHERE id=?", (gid, row_id))
            updated.append(f"  {tag} -> {gid}")
        else:
            not_found.append(tag)

    conn.commit()
    conn.close()

    if renamed:
        print(f"Renamed {len(renamed)} tags:")
        for line in renamed:
            print(line)

    print(f"\nUpdated {len(updated)} clients:")
    for line in updated:
        print(line)

    print(f"\nNot found ({len(not_found)}): {', '.join(not_found) if not_found else 'none'}")
    print("\nDone!")

if __name__ == '__main__':
    main()

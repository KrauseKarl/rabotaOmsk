import json
with open('db/json_files/professions.json', encoding='utf-8') as js_file:
    categories_dict = json.load(js_file)

# categories_dict = {
#     "1": "менеджер по продажам",
#     "2": "строитель",
#     "3": "курьер",
#     "4": "промоутер",
#     "5": "администратор",
#     "6": "дизайнер, художник"
# }
# professions = {}
# with open('base_professions.txt', 'r', encoding='utf-8') as f:
#     base_prof = f.read().splitlines()
# with open('all_professions.txt', 'r', encoding='utf-8') as all_file:
#     all_prof = all_file.read().splitlines()
#
#
# with open('json_files/all.json', 'w', encoding='utf-8') as js_file:
#     basedict = {}
#     for string in all_prof:
#         if not string.startswith('\t'):
#             key = string
#             basedict[key] = []
#         else:
#             basedict[key].append(string.strip())
#     json.dump(basedict, js_file, ensure_ascii=False, indent=4)
#
# prof = {}
#
# with open('json_files/all.json', encoding='utf-8') as js_file:
#     file = json.load(js_file)
#     count = 1
#     for k, v in file.items():
#         prof[count] = {k: {}}
#         for ind, sub in enumerate(v):
#             sub_key = f"{count}0{ind}"
#             bub = {sub_key: sub}
#             prof[count][k].update(bub)
#         count += 1
#
# with open('json_files/professions.json', 'w', encoding='utf-8') as js_file:
#     json.dump(prof, js_file, ensure_ascii=False, indent=4)
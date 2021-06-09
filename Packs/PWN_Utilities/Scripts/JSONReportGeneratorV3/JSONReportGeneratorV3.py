import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401
import json

data = demisto.args()['json'] if 'json' in demisto.args() else demisto.context()
titleKey = demisto.args()['titleKey'] if 'titleKey' in demisto.args() else None
title = demisto.args()['title'] if 'title' in demisto.args() else None

excludeKeys = demisto.args()['excludeKeys'].split(",") if 'excludeKeys' in demisto.args() else []

if titleKey and "." in titleKey:
    l = titleKey.split(".")
    titleKey = data[l[0]]

    if len(l) > 1:
        l.pop(0)
        for i in l:
            titleKey = titleKey[i]
elif titleKey:
    titleKey = data[titleKey]

elif title:
    titleKey = title
else:
    titleKey = "Report"

md = f"# {titleKey}\n\n"

for k, v in data.items():
    if k in excludeKeys:
        continue
    if isinstance(v, list):
        md += f"**{k}**\n"
        md += "\n".join(v)
    elif isinstance(v, dict):
        md += "\n"
        md += f"\n**{k}**\n"
        md += json.dumps(v).replace("\",", "\n").replace("{", "\n").replace("}", "").replace(
            "\\n", "\n").replace("[", "\n").replace("]", "\n").replace(", \"", "\n").replace("\"", "")
        md += "\n"
    else:
        md += f"\n**{k}** "
        md += f"{str(v)}\n"

entry = {
    'Type': 1,
    'Contents': md,
    'ContentsFormat': 'markdown',
    'HumanReadable': md,
    'ReadableContentsFormat': 'markdown'
}


demisto.results(entry)

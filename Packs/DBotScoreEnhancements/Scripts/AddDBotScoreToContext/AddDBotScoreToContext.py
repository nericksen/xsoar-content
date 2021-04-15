import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401
indicator = demisto.args().get("indicator")
indicatorType = demisto.args().get("indicatorType")
score = int(demisto.args().get("score"))
vendor = demisto.args().get("vendor")
reliability = demisto.args().get("reliability", None)

dbotscore = {
    "Indicator": indicator,
    "Type": indicatorType,
    "Vendor": vendor,
    "Score": score,
    "Reliability": reliability
}

md = tableToMarkdown("Indicator", dbotscore)

entry = {
    "Type": entryTypes["note"],
    "ContentsFormat": formats["json"],
    "Contents": dbotscore,
    "EntryContext": {"DBotScore": dbotscore},
    "HumanReadble": md
}

demisto.results(entry)

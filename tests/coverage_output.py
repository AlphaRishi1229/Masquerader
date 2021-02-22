"""Convert coverage report from xml to json using below code."""
import json
import xml.etree.ElementTree as ET

tree = ET.parse("reports/pytest/coverage_xml/index.xml")
attrib = tree.getroot().attrib
out = {
    "coverage_pct": float(attrib.get("line-rate")) * 100,  # type: ignore
    "lines_total": int(attrib.get("lines-valid")),  # type: ignore
    "lines_covered": int(attrib.get("lines-covered")),  # type: ignore
    "branch_pct": int(attrib.get("branch-rate")),  # type: ignore
    "branches_covered": int(attrib.get("branches-covered")),  # type: ignore
    "branches_total": int(attrib.get("branches-valid")),  # type: ignore
}

with open("coverage/coverage_output.json", "w") as outfile:
    json.dump(out, outfile)
    outfile.close()

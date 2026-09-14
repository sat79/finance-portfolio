"""Read saved XLSX values with the standard library; does not evaluate formulas."""
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read_xlsx(path: Path) -> dict:
    with ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"Corrupt XLSX member: {bad}")
        if any(p.startswith("xl/externalLinks/") or p.endswith("vbaProject.bin")
               for p in archive.namelist()):
            raise ValueError("Unexpected external workbook link or macro")
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ["".join(e.itertext()) for e in ET.fromstring(
                archive.read("xl/sharedStrings.xml"))]
        relationships = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        output = {}
        for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS):
            target = relationships[sheet.attrib[RID]]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            cells = {}
            for cell in ET.fromstring(archive.read(member)).findall(".//s:sheetData/s:row/s:c", NS):
                kind = cell.attrib.get("t")
                raw = cell.findtext("s:v", default=None, namespaces=NS)
                if kind == "e":
                    raise ValueError(f"Excel error: {sheet.attrib['name']}!{cell.attrib['r']}: {raw}")
                if kind == "s":
                    value = strings[int(raw)]
                elif kind == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                elif kind in ("str", "b") or raw is None:
                    value = raw
                else:
                    value = float(raw)
                cells[cell.attrib["r"]] = {
                    "value": value, "formula": cell.findtext("s:f", namespaces=NS)}
            output[sheet.attrib["name"]] = cells
        return output

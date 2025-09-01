
import os
import json
from bs4 import BeautifulSoup

def log(msg):
    print(f"::notice::{msg}")

log("Starting docs JSON export...")
folders = [
    "docs/_build/html/api",
    "docs/_build/html/ext",
]
result = {}
try:
    for folder in folders:
        if not os.path.isdir(folder):
            log(f"Skipping missing folder: {folder}")
            continue
        base_html = os.path.normpath("docs/_build/html")
        for root, _, files in os.walk(folder):
            rel_dir = os.path.relpath(root, base_html).replace("\\", "/") + "/"
            if rel_dir not in result:
                result[rel_dir] = {}
            for html_file in files:
                if not html_file.endswith(".html"):
                    continue
                file_path = os.path.join(root, html_file)
                with open(file_path, encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
                    page_index = {}
                    for class_dl in soup.find_all("dl", class_="class"):
                        dt = class_dl.find("dt")
                        class_name = dt.get("id") if dt else None
                        if not class_name:
                            class_name = dt.text.split(":")[-1].strip() if dt else None
                        members = []
                        for member_dl in class_dl.find_all("dl", class_=["attribute", "method"]):
                            for member_dt in member_dl.find_all("dt"):
                                member_id = member_dt.get("id")
                                member_name = member_id.split(".")[-1] if member_id else member_dt.text.split(":")[-1].strip()
                                if member_name:
                                    members.append(member_name)
                        page_index[class_name] = members
                    for func_dl in soup.find_all("dl", class_="function"):
                        dt = func_dl.find("dt")
                        func_name = dt.get("id") if dt else None
                        if not func_name:
                            func_name = dt.text.split(":")[-1].strip() if dt else None
                        page_index[func_name] = []
                    result[rel_dir][html_file] = page_index
    cleaned_result = {k: v for k, v in result.items() if v}
    with open("docs.json", "w", encoding="utf-8") as out:
        json.dump(cleaned_result, out, indent=2, ensure_ascii=False)
    log("Exported docs to docs.json")
    log("To upload as artifact: docs.json")
except Exception as e:
    print(f"::error::Docs JSON export failed: {e}")
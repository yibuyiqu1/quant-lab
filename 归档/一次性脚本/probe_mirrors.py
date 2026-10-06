# -*- coding: utf-8 -*-
"""探测失效资料的可用镜像：查 GitHub 仓库目录、releases 资源与备用站点。"""
import json
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def show_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    try:
        data = json.loads(get(url))
    except Exception as exc:  # noqa: BLE001
        print(f"[{repo}/{path}] ERR {type(exc).__name__}: {exc}")
        return
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if item.get("type") == "file" and item.get("size", 0) > 200_000:
            print(f"  {item['size']//1024:>6}KB  {item['path']}")
        elif item.get("type") == "dir":
            print(f"  <dir>        {item['path']}/")


def show_releases(repo):
    try:
        data = json.loads(get(f"https://api.github.com/repos/{repo}/releases"))
    except Exception as exc:  # noqa: BLE001
        print(f"[{repo}] releases ERR {type(exc).__name__}: {exc}")
        return
    for rel in data[:3]:
        print(f"  release {rel.get('tag_name')}")
        for asset in rel.get("assets", []):
            print(f"    {asset['size']//1024:>6}KB  {asset['name']}  <- {asset['browser_download_url']}")


for repo, path in [
    ("nndl/nndl.github.io", ""),
    ("nndl/nndl.github.io", "docs"),
    ("szcf-weiya/ESL-CN", ""),
    ("szcf-weiya/ESL-CN", "docs"),
    ("datawhalechina/pumpkin-book", ""),
    ("probml/pml-book", ""),
]:
    print(f"\n=== {repo}/{path}")
    show_tree(repo, path)

print("\n=== releases")
for repo in ["nndl/nndl.github.io", "szcf-weiya/ESL-CN", "datawhalechina/pumpkin-book", "probml/pml-book"]:
    print(f"\n-- {repo}")
    show_releases(repo)

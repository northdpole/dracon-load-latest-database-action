
import requests
from dateutil import parser
import os
import zipfile
from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
repo=f"https://api.github.com/repos/{os.environ['INPUT_REPO']}/actions/artifacts"

print(f"retrieving artifacts from repo {repo}")

artifacts = requests.get(repo).json()['artifacts']
latest = parser.isoparse(artifacts[-1]['updated_at'])
artifact_url = artifacts[-1]["archive_download_url"]
for art in artifacts:
    if "dracon_enrichment_db" not in art["name"]:
        continue
    d =parser.isoparse(art['updated_at'])
    if d > latest:
        latest = d
        artifact_url = art["archive_download_url"]

pprint( os.environ["ACTIONS_RUNTIME_TOKEN"] == os.environ["INPUT_GH_ACCESS_TOKEN"])
token = os.environ["ACTIONS_RUNTIME_TOKEN"] # os.environ["INPUT_GH_ACCESS_TOKEN"]
for name, token in {"ACTIONS_RUNTIME_TOKEN": os.environ["ACTIONS_RUNTIME_TOKEN"],"INPUT_GH_ACCESS_TOKEN": os.environ["INPUT_GH_ACCESS_TOKEN"]}.items():
    pprint(f"Trying with {name}")
    if len(token) == 0:
        pprint("empty token")
    resp = requests.get(artifact_url, stream=True,headers={"Authorization" :"token %s"%token})
    if resp.status_code == 200:
        break
if resp.status_code != 200:
    print("Error receiving files for artifact %s"%artifact_url)
    pprint(requests.get(artifact_url).json())
    raise ValueError

with open("/tmp/latest.zip", "wb") as fl:
    for chunk in resp.iter_content():
        fl.write(chunk)
try:
    with zipfile.ZipFile("/tmp/latest.zip") as zip:
        print("Extracting files to %s"%os.environ["INPUT_OUTPUT_DIR"])
        zip.extractall(os.environ["INPUT_OUTPUT_DIR"])

    print("Files extracted, dir contents are:")
    pprint(os.listdir(os.environ["INPUT_OUTPUT_DIR"]))
except zipfile.BadZipFile as bzf:
    with open("/tmp/latest.zip") as l:
        pprint(l.read())
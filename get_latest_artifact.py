import requests
from dateutil import parser
import os
import zipfile
from pprint import pprint

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

token = os.environ["INPUT_GH_ACCESS_TOKEN"]
header={"Authorization" :"token %s"%token}
resp = requests.get(artifact_url, stream=True,headers=header)
pprint(resp.status_code)
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
    # print("Could not download the artifact as zip message was: %s"%resp.json())
    # pprint(resp.text)
    with open("/tmp/latest.zip") as l:
        pprint(l.read())
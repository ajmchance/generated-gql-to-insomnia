import re
import argparse
from dataclasses import dataclass, field
from time import time
import json
import uuid
import os

gql_regex = re.compile(r"/\*\n(query[^;]*)\*/\n", re.MULTILINE)
name_regex = r"query (.*?)[ (]"
camel_regex = r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))"
variable_name_regex = r"\$(.*?):[^{]*?\n"


@dataclass
class InsomniaRequest:
    modified: int
    created: int
    name: str
    _id: str
    parentId: str
    headers: list = field(
        default_factory=lambda: [
            {
                "id": "pair_" + uuid.uuid4().hex,
                "name": "Content-Type",
                "value": "application/json",
            },
            {
                "id": "pair_" + uuid.uuid4().hex,
                "name": "Device-Auth-Token",
                "value": "{{ ## REPLACE ME}}",
            },
        ]
    )
    description: str = ""
    url: str = "http://0.0.0.0:8000/"
    method: str = "POST"
    body: dict = field(
        default_factory=lambda: {"mimeType": "application/graphql", "text": None}
    )
    parameters: list = field(
        default_factory=lambda: [
            {
                "id": "pair_" + uuid.uuid4().hex,
                "name": "",
                "value": "",
                "description": "",
            }
        ]
    )
    isPrivate: bool = False
    settingSendCookies: bool = True
    settingFollowRedirects: str = "global"
    _type: str = "request"
    authentication: dict = field(default_factory=lambda: {})
    settingStoreCookies: bool = True
    settingDisableRenderRequestBody: bool = True
    settingEncodeUrl: bool = True
    settingRebuildPath: bool = True


def main(path: str, out: str, secret: str, wrk_name: str, url:str):
    now = int(time())
    folder_ids = {}
    export_info = {
        "_type": "export",
        "__export_format": 4,
        "__export_date": now,
        "__export_source": "insomnia.desktop.app:v2021.6.0",  # computers are easy to lie to
    }
    wrk_id = "wrk_" + uuid.uuid4().hex
    resources = [
        {
            "_id": wrk_id,
            "parentId": None,
            "modified": now,
            "created": now,
            "name": wrk_name,
            "description": "",
            "scope": "collection",
            "_type": "workspace",
        },
    ]
    for inputfile in os.listdir(path):
        with open(path + str(inputfile), "r") as gqlFile:
            file_content = gqlFile.read()
            foldername = re.findall(camel_regex, str(inputfile))[0]
            if not foldername in folder_ids:
                folder_id = "wrk_" + uuid.uuid4().hex
                folder_ids[foldername] = folder_id
                resources.append(
                    {
                        "_id": folder_id,
                        "parentId": wrk_id,
                        "modified": now,
                        "created": now,
                        "name": foldername,
                        "description": "",
                        "environment": {},
                        "environmentPropertyOrder": None,
                        "_type": "request_group",
                    }
                )
            else:
                folder_id = folder_ids[foldername]

            match = re.findall(gql_regex, file_content)

            if match:
                name = re.match(name_regex, match[0])
                variables_found = re.findall(variable_name_regex, match[0])
                variables = {}
                for v in variables_found:
                    variables[v] = None
                to_append = InsomniaRequest(
                    _id="req_" + str(uuid.uuid4().hex),
                    parentId=folder_id,
                    modified=now,
                    created=now,
                    name=name[0].split(" ")[1][:-1],  # ugly
                    url=url
                )
                to_append.headers[1]["value"] = "{{_." + secret + "}}"
                to_append.body["text"] = json.dumps(
                    {"query": match[0], "variables": variables}
                )
                resources.append(to_append.__dict__)

    export_info["resources"] = resources
    with open(out, "w") as outfile:
        outfile.write(json.dumps(export_info))
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--path", help="input filepath to generated folder", default="./"
    )
    parser.add_argument("-o", "--out", help="output file", default="out/insomnia.json")
    parser.add_argument(
        "-s",
        "--secret",
        help="secret key name in your environment",
        default="SECRETKEY",
    )
    parser.add_argument(
        "-n", "--name", help="workspace name", default="insomnia export"
    )
    parser.add_argument(
        "-u", "--url", help="default url", default="http://0.0.0.0:8000"
    )
    args = parser.parse_args()
    main(
        path=args.path,
        out=args.out,
        secret=args.secret,
        wrk_name=args.name,
        url=args.url
    )



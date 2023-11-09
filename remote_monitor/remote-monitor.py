import requests
import msal
import atexit
import os.path
import urllib.parse
import sys
import time
import yaml
from typing import List, Tuple


"""
.rc file format (yaml)
    sharepoint-host: ""
    sharepoint-site: ""
    sharepoint-client-id: ""
    sharepoint-tenant-id: ""
    sharepoint-base-dir: "'
    download-dir: ""
    poll-period: ""
environment variables
    sharepoint-client-secret
cmdline format
    > python3 remote-monitor.py --sharepoint-host=http://a.com --rc-file=./myconfig.rc

notes
    - a configuration can come from rc file, env variable or commandline. there are two special configurations to consider, rc-file and sharepoint-client-secret. rcfile can only come from commandline and client_secret can only come from env variable. all other configurations can be from any of the three sources.
    - be default, the program expects .remote-monitor.rc file in user's HOME dir; user can override it using commandline
"""

def _load_config_from_dict(expected: dict, received: dict) -> dict:
    try:
        extracted: dict = dict(
            [
                (k, expected[k][0](received[k]))
                for k in expected.keys()
                if k in received
            ]
        )
    except Exception as e:
        raise ValueError("Looks like some configuration is incorrent", e)

    return extracted


def load_program_configurations(expected_cfg: dict) -> dict:
    program_config: dict = {}
    defaults: dict = dict(
        [
            (k, expected_cfg[k][1])
            for k in expected_cfg.keys()
            if expected_cfg[k][1] is not None
        ]
    )
    cmdline_dict: dict = dict(
        [tuple(pair.strip("-").split("=")) for pair in sys.argv[1:]]    #type: ignore
    )
    cmdline_config = _load_config_from_dict(expected_cfg, cmdline_dict)

    env_config: dict = _load_config_from_dict(expected_cfg, dict(os.environ))

    with open(cmdline_dict['rc-file']) as fp:
        rc_config = _load_config_from_dict(expected_cfg, yaml.safe_load(fp))

    return defaults | env_config | rc_config | cmdline_config


def prepare_remote_access() -> dict:
    remote_info: dict = {}
    pd = program_data
    ep = pd['sharepoint-endpoint']
    host = pd['sharepoint-host']
    site = pd['sharepoint-site']

    cache = msal.SerializableTokenCache()
    app = msal.ConfidentialClientApplication(
        client_id=pd['sharepoint-client-id'],
        client_credential=pd["sharepoint-client-secret"],
        authority=pd["authority"],
        token_cache=cache
    )
    accounts = app.get_accounts()
    if len(accounts) > 0:
        result = app.acquire_token_silent(pd['scopes'], account=accounts[0])
    else:
        result = app.acquire_token_for_client(scopes=pd['scopes'])

    if "access_token" not in result:
        raise Exception("Failed to get access token")

    remote_info['access_token'] = result['access_token']
    headers = {"Authorization": "Bearer " + result["access_token"]}
    result = requests.get(
        f"{ep}/sites/{host}:/sites/{site}",
        headers=headers
    )
    site_info = result.json()
    remote_info['site_id'] = site_info["id"]

    result = requests.get(f"{ep}/sites/{site}/drive", headers=headers)
    drive_info = result.json()
    remote_info['drive_id'] = drive_info["id"]

    return remote_info


def ls_remote() -> List[Tuple[str, str]]:
    ep = program_data['sharepoint-endpoint']
    folder_url = urllib.parse.quote(program_data['sharepoint-base-dir'])
    drive_id = program_data['sharepoint-drive-id']
    header = headers = {
        "Authorization": "Bearer " + program_data["access_token"]
    }

    folder_id_url = f"{ep}/drives/{drive_id}/root:/{folder_url}"
    result = requests.get(folder_id_url, headers=headers)
    result.raise_for_status()
    folder_info = result.json()
    folder_id = folder_info["id"]

    ls_url =  f"{ep}/drives/{drive_id}/items/{folder_id}/children"
    result = requests.get(ls_url,headers=headers)
    result.raise_for_status()
    fileobjects = list(
        filter(
            lambda x: 'folder' not in x,
            result.json()["value"]
        )
    )
    return [
        (x.get('name'), x.get("@microsoft.graph.downloadUrl"))
        for x in fileobjects
    ]


def ls_local() -> list:
    downloaded_files: list = []
    ledger_filename = program_data['ledger_file']
    try:
        downloaded_files = open(ledger_filename).read().split("\n")
    except:
        pass
    return downloaded_files


def ls_new_files(remote_files: list, local_files: list) -> list:
    return list(set(remote_files) - set(local_files))


def download_single_file(filename: str, download_url: str) -> dict:
    response = requests.get(download_url)
    download_fqn = os.path.join(program_data['download_dir'], filename)
    with open(download_fqn, "wb") as f:
        f.write(response.content)
    summary = {
        "property": "",
        "doctype": "",
        "query_file": download_fqn,
        "timestamp": time.time()
    }
    return summary


def update_download_ledger(download_summary: dict) -> bool:
    ledger_filename = program_data['ledger_file']
    try:
        with open(ledger_filename, "a+") as fp:
            print(download_summary, file=fp)
    except:
        return False
    return True


def download(to_download: List[Tuple[str, str]]) -> None:
    [
        update_download_ledger(
            download_single_file(f[0], f[1])
        ) for f in to_download
    ]
    return


if __name__ == '__main__':
    expected_config = {
        #"configuration-name": (datatype, default_value(None means mandatory))
        "sharepoint-host": (str, None),
        "sharepoint-site": (str, None),
        "sharepoint-client-id": (str, None),
        "sharepoint-tenant-id": (str, None),
        "sharepoint-base-dir": (str, None),
        "sharepoint-endpoint": (str, None),
        "download-dir": (str, None),
        "sharepoint-client-secret": (str, None),
        "rc_file": (
            str,
            os.path.join(
                os.environ['HOME'],
                "." + os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".rc"
            )
        ),
    }
    program_data: dict = load_program_configurations(expected_config)
    program_data.update(prepare_remote_access())
    all_local_files: list = ls_local()

    while True:
        polled_at = time.time()
        download(ls_new_files(ls_local(), ls_remote()))
        poll_period = program_data['user_cfg']['poll-period']
        wait_sec = max(0, poll_period - (time.time() - polled_at))
        time.sleep(wait_sec)
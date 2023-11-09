import requests
import msal
from msal import ConfidentialClientApplication
import atexit
import os.path
import urllib.parse
import argparse
import time

# parser = argparse.ArgumentParser()
# parser.add_argument("--download_dir", help="folder directory")
# parser.add_argument("--poll_interval", help=" scheduler time in seconds")
# args = parser.parse_args()

# path_location = args.path
folder_path = "documents" # replace this with the folder you want to list
tenant_id = '39c7f15b-5f6f-4bab-8ab5-0b6e414bdd83'
client_id = '8433780e-598f-4f92-8d31-80391ff86891'
client_secret = 'm6U8Q~ciyahATSY1AHGHOP8BeI2pIhmLtncoXa4c'
share_point_host = 'pvrt613.sharepoint.com'
site_name = "ai-team"
authority = "https://login.microsoftonline.com/" + tenant_id
end_point = "https://graph.microsoft.com/v1.0"
scopes = ["https://graph.microsoft.com/.default"]
file_list = []
property_name=""
file_id_list = []

# get the folder id
def get_files(folder_name, drive_id, headers, stage, parent_folder, file_list, property_name, file_id_list): 
    folder_path = folder_name
    folder_url = urllib.parse.quote(folder_path)
    result = requests.get(
        f"{end_point}/drives/{drive_id}/root:/{folder_url}", headers=headers
    )
    result.raise_for_status()
    folder_info = result.json()
    folder_id = folder_info["id"]

    result = requests.get(
        f"{end_point}/drives/{drive_id}/items/{folder_id}/children",
        headers=headers,
    )
    result.raise_for_status()
    children = result.json()["value"]
    return_result = []
    stage += 1
    for file in children:
        file_name = file.get("name")
        if "folder" not in file: 
            if file.get("id") not in file_id_list: 
                print({"property" : property_name, "doc_type" : parent_folder , "name" : file_name})
                file_download = file.get("@microsoft.graph.downloadUrl")
                response = requests.get(file_download)
                save_to_path = os.path.join("/Users/sumitkumar/Desktop/noun_adjective",file_name)
                with open(save_to_path, "wb") as f:
                    f.write(response.content)
                    file_id_list.append(file.get("id"))
                    return_result.append({ "folder": False, "name": file_name, "path": folder_name, "parent": parent_folder, "stage": stage})
        else:
            file_info = { "folder": True, "name": file_name, "stage": stage }
            if stage > 1:
                file_info['parent'] = parent_folder
                file_info['path'] = folder_name
            if stage ==2:
                property_name = parent_folder

            return_result.append(file_info)
            next_result = get_files(folder_name + "/" + file_name, drive_id, headers, stage, file_name, file_list, property_name, file_id_list)
            return_result += next_result 
    return return_result    


def get_file_from_sharepoint():
    try:
        cache = msal.SerializableTokenCache()

        if os.path.exists("token_cache.bin"):
            cache.deserialize(open("token_cache.bin", "r").read())

        atexit.register(
            lambda: open("token_cache.bin", "w").write(cache.serialize())
            if cache.has_state_changed
            else None
        )

        app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
            token_cache=cache,
        )

        accounts = app.get_accounts()
        result = None

        if len(accounts) > 0:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        if not result:
            result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            headers = {"Authorization": "Bearer " + result["access_token"]}
            # get the site id
            result = requests.get(
                f"{end_point}/sites/{share_point_host}:/sites/{site_name}",
                headers=headers,
            )
            result.raise_for_status()
            site_info = result.json()
            site_id = site_info["id"]

            # get the drive id
            result = requests.get(f"{end_point}/sites/{site_id}/drive", headers=headers)
            result.raise_for_status()
            drive_info = result.json()
            drive_id = drive_info["id"]
            file_list1 = get_files(folder_path, drive_id, headers, 0, "", file_list, property_name, file_id_list)
            file_list.extend(file_list1)
        else:
            raise Exception("no access token in result")

    except Exception as e:
        print("The exception is: ", e)

while True:
    get_file_from_sharepoint()
    time.sleep(2)

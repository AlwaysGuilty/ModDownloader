#!"D:\Minecraft\Scripts\python.exe"

import sys
import os
import requests
import shutil


"""
Change only these:
"""
mc_version = "1.19.3"
mod_list = "mod_list_1193.txt"
#mod_dir = "C:\Users\%username%\AppData\Roaming\.minecraft\mods"
#mod_dir = f"D:\Minecraft\MultiMC\instances\{mc_version}\.minecraft\mods"
mod_dir = "D:\Minecraft\MultiMC\instances\\test\.minecraft\mods"



# curseforge api key
API_KEY = "$2a$10$Y1FpCvUnvpejIjnADeYDtuoBphtPRmlRub5NKn9Z.sEn3.DySM7Ee"
curseforge_api_url = "https://api.curseforge.com"


# def process_input():
#     if len(sys.argv) != 2:
#         print("Usage: get_mods.py <minecraft version>")
#         sys.exit(1)
#     mc_version = sys.argv[1]
#     assert mc_version in ["1.19.2", "1.19.3"], "Invalid version"


def clean_mods_dir():
    print("Removing existing mods...")
    for f in os.listdir(mod_dir):
        path = os.path.join(mod_dir, f)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)        
        except Exception as e:
            print(f"Failed to remove a mod: {f}, reason: {e}")
            sys.exit(1)


def main():
    # github and midrinth also have apis, might implement that at some point in the future
    # downside of github api: can't track minecraft version of the mod
    github_mods =["biome-thread-local-fix", "force-port", "sleep-background"]
    
    # remove existing mods
    clean_mods_dir()

    # read mod list
    mods = []
    try:
        with open(mod_list, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                mods.append(line.strip().split(","))
        f.close()
    except Exception as e:
        print(f"Failed to read the mod list: {e}")
        sys.exit(1)


    # iterate through mod list
    for i, mod in enumerate(mods):
        ticker = f"[{i+1}/{len(mods)}]"

        if mod[0] in github_mods:
            print(f"{ticker} Downloading {mod[0]} from github...")
            dl_link = mod[1]
        else:
            print(f"{ticker} Downloading {mod[0]} from curseforge...")
            # curseforge mods
            # obtain download mod data
            headers = {
                "Accept": "application/json",
                "x-api-key": API_KEY
            }
            params = {
                "gameId": 432,
                "gameVersion": mc_version,
                "modLoaderType": 4,
                "slug": mod[0]
            }
            res = requests.get(curseforge_api_url + "/v1/mods/search", params=params, headers=headers)
            assert res.status_code == 200, "Failed to fetch mod data from CurseForge API"
                    
            # extract correct modId and fileId from latestFilesIndexes field
            res = res.json()
            modId = res["data"][0]["id"]
            files = res["data"][0]["latestFilesIndexes"]
            candidates = [x for x in files if x["gameVersion"] == mc_version and x["modLoader"] == 4]
            fileId = candidates[0]["fileId"]

            # get download link from curseforge api
            res = requests.get(curseforge_api_url + f"/v1/mods/{modId}/files/{fileId}", headers=headers)
            assert res.status_code == 200, "Failed to fetch download URL from CurseForge API"
            dl_link = res.json()["data"]["downloadUrl"]
    
        # download mod
        res = requests.get(dl_link, allow_redirects=True)
        assert res.status_code == 200, "Failed to download mod"
        print(f"{ticker} Downloaded {mod[0]} successfully")

        # save mod to a file
        save_path = os.path.join(mod_dir, mod[0] + ".jar")
        with open(save_path, "wb") as mf:
            mf.write(res.content)
        mf.close()
        print(f"{ticker} Saved {mod[0]} to {save_path}")


if __name__ == "__main__":
    main()
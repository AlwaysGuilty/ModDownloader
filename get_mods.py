#!"D:\Minecraft\Scripts\python.exe"

import sys
import os
import requests
import shutil
import dotenv


"""
Change only these:
"""
mc_version = "1.19.3"
mod_list = "mod_list.txt"
#mod_dir = "C:\Users\%username%\AppData\Roaming\.minecraft\mods"
#mod_dir = f"D:\Minecraft\MultiMC\instances\{mc_version}\.minecraft\mods"
mod_dir = "D:\Minecraft\MultiMC\instances\\test\.minecraft\mods"


dotenv.load_dotenv()
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")
EMAIL = os.getenv("EMAIL")
modrinth_api_url = "https://api.modrinth.com/v2"
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


def read_mod_list(path: str) -> list:
    mods = []
    try:
        with open(path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                mods.append(line.strip().split(","))
        f.close()
    except Exception as e:
        print(f"Failed to read the mod list: {e}")
        sys.exit(1)
    return mods


def main():
    # order of requests: modrinth, curseforge, github

    # github and modrinth also have apis, might implement that at some point in the future
    # downside of github api: can't track minecraft version of the mod and the mod loader it uses
    github_mods = ["biome-thread-local-fix", "force-port", "sleep-background"]
    github_mods_links = ["https://github.com/RedLime/BiomeThreadLocalFix/releases/download/1.3/BiomeThreadLocalFix-1.3.jar", "https://github.com/DuncanRuns/Force-Port-Mod/releases/download/v1.1.0/forceport-1.1.0.jar", "https://github.com/RedLime/SleepBackground/releases/download/3.8/sleepbackground-3.8-1.15.x-1.19.x.jar"]
    
    # remove existing mods
    clean_mods_dir()

    # read mod list
    mods = read_mod_list(mod_list)

    # iterate through mod list
    for i, mod in enumerate(mods):
        ticker = f"[{i+1}/{len(mods)}]"

        if mod[0] in github_mods:
            print(f"{ticker} Downloading {mod[0]} from GitHub...")
            dl_link = mod[1]
        else:
            # attempt to download from modrinth
            print(f"{ticker} Searching for {mod[0]} on Modrinth...")
            headers = {
                "User-Agent": f"AlwaysGuilty/ModDownloader ({EMAIL})"
            }

            ##

            # modrinth code here

            ##


            print(f"{ticker} Downloading {mod[0]} from CurseForge...")
            
            # obtain mod data
            headers = {
                "Accept": "application/json",
                "x-api-key": CURSEFORGE_API_KEY
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
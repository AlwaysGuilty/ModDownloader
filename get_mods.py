#!"D:\Minecraft\Scripts\python.exe"

import sys
import os
import requests
import shutil
import dotenv
from enum import Enum


# supported mod loaders are intersection of those supported by both platforms
# format: (CurseForge enum, Modrinth name)
class ModLoader(Enum):
    FORGE = (1, "forge")
    LITELOADER = (3, "liteLoader")
    FABRIC = (4, "fabric")
    QUILT = (5, "quilt")


"""
When running the cript, change only these:
"""
mc_version = "1.19.3"
mod_list = "mod_list.txt"
#mod_dir = "C:\Users\%username%\AppData\Roaming\.minecraft\mods"
mod_dir = f"D:\Minecraft\MultiMC\instances\\test\.minecraft\mods"
mod_loader = ModLoader.FABRIC.value


# load environ vars from .env file or just change them here
dotenv.load_dotenv()
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")
EMAIL = os.getenv("EMAIL")


modrinth_api_url = "https://api.modrinth.com/v2"
curseforge_api_url = "https://api.curseforge.com"
ticker = ""
num_completed = 0


def log(msg: str):
    print(f"{ticker} {msg}")


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
            print(f"Failed to remove {f}, reason: {e}")
            sys.exit(1)


def read_mod_list(path: str) -> list:
    mods = []
    try:
        with open(path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                mods.append(line.strip())
        f.close()
    except Exception as e:
        print(f"Failed to read the mod list: {e}")
        sys.exit(1)
    return mods


def get_from_modrinth(mod: str) -> tuple:
    log(f"Searching for {mod} on Modrinth...")
    headers = {
        "User-Agent": f"AlwaysGuilty/ModDownloader ({EMAIL})"
    }
    # params = {
    #     "query": mod,
    #     "facets": "[['categories:fabric'], ['versions:" + mc_version + "'], ['project_type:mod']]"
    # }

    # res = requests.get(modrinth_api_url + "/search", headers=headers, params=params)
    # assert res.status_code == 200, "Failed to fetch mod data from Modrinth API"
    # res = res.json()
    # # iterate through results
    # mod_found = False
    # for i, result in enumerate(res["hits"]):
    #     if result["slug"] == mod:
    #         mod_found = True
    # print(f"{ticker} Found {mod} on Modrinth!")
    params = {
        "loaders": "['" + mod_loader[1] + "']",
        "game_versions": "[\"" + mc_version + "\"]"
    }
    url = modrinth_api_url + "/project/" + mod + "/version"
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        log(f"Failed to find {mod} on Modrinth")
        return None
    res = res.json()
    dl_link = res[0]["files"][0]["url"]
    filename = res[0]["files"][0]["filename"]
    return dl_link, filename


def get_from_curseforge(mod: str) -> tuple:
    log(f"Searching for {mod} on CurseForge...")
    headers = {
        "Accept": "application/json",
        "x-api-key": CURSEFORGE_API_KEY
    }
    params = {
        "gameId": 432,
        "gameVersion": mc_version,
        "modLoaderType": mod_loader[0],
        "slug": mod
    }
    url = curseforge_api_url + "/v1/mods/search"
    res = requests.get(url, params=params, headers=headers)
    if res.status_code != 200:
        log(f"Failed to find {mod} on CurseForge")
        return None
    
    # iterate through results to find the correct mod, only searches for an exact match
    res = res.json()
    mod_found = False
    mod_idx = 0
    for i, result in enumerate(res["data"]):
        if result["slug"] == mod:
            mod_found = True
            mod_idx = i
            break
    if not mod_found:
        log(f"Failed to find {mod} on CurseForge")
        return None

    # extract modId, fileId and filename
    modId = res["data"][mod_idx]["id"]
    files = res["data"][mod_idx]["latestFilesIndexes"]
    candidates = [x for x in files if x["gameVersion"] == mc_version and x["modLoader"] == mod_loader[0]]
    fileId = candidates[mod_idx]["fileId"]
    filename = candidates[mod_idx]["filename"]

    # get download URL from curseforge api
    url = curseforge_api_url + f"/v1/mods/{modId}/files/{fileId}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        log(f"Failed to fetch download URL for {mod} from CurseForge API")
        return None
    dl_link = res.json()["data"]["downloadUrl"]
    return dl_link, filename


# ugly, i know
# note: sleepbackground causes game to hang when creating a new world in 1.19.2 and 1.19.3. Therefore it's recommended to use DynamicFPS (slug: dynamic-fps) instead
def get_from_github(mod:str) -> tuple:
    github_mods = ["biome-thread-local-fix", "force-port", "sleep-background"]
    github_mods_links = ["https://github.com/RedLime/BiomeThreadLocalFix/releases/download/1.3/BiomeThreadLocalFix-1.3.jar", "https://github.com/DuncanRuns/Force-Port-Mod/releases/download/v1.1.0/forceport-1.1.0.jar", "https://github.com/RedLime/SleepBackground/releases/download/3.8/sleepbackground-3.8-1.15.x-1.19.x.jar"]
    log(f"Searching for {mod} on GitHub...")
    for i, entry in enumerate(github_mods):
        if entry == mod:
            return github_mods_links[i], mod + ".jar"
    log(f"Failed to find {mod} on GitHub")
    return None


def dl_mod(dl_link: str, slug: str, filename: str):
    log(f"Downloading {slug}...")
    res = requests.get(dl_link, allow_redirects=True)
    if res.status_code != 200:
        log(f"Failed to download {slug}")
        return
    log(f"Downloaded {slug} successfully")

    try:
        save_path = os.path.join(mod_dir, filename)
        with open(save_path, "wb") as mf:
            mf.write(res.content)
        mf.close()
        log(f"Saved {slug} to {save_path}")
    except Exception as e:
        log(f"Failed to save {slug} into {filename}: {e}")


def main():
    global ticker
    global num_completed

    # remove existing mods
    clean_mods_dir()

    # read mod list
    mods = read_mod_list(mod_list)

    # iterate through mod list
    for i, mod in enumerate(mods):
        ticker = f"[{i + 1}/{len(mods)}]"

        # order of requests: modrinth, curseforge, github
        # search until we find a mod, if we don't find it, skip it

        retval = get_from_modrinth(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            num_completed += 1
            continue

        retval = get_from_curseforge(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            num_completed += 1
            continue

        retval = get_from_github(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            num_completed += 1
            continue

        log(f"Failed to find {mod}, skipping...")
    print(f"Successfully downloaded {num_completed}/{len(mods)} mods")

if __name__ == "__main__":
    main()
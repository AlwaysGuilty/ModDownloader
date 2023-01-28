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
ticker = ""


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
            print(f"Failed to remove a mod: {f}, reason: {e}")
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
    #     "facets": "[[\"categories:fabric\"], [\"versions:" + mc_version + "\"], [\"project_type:mod\"]]"
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
        "loaders": "[\"fabric\"]",
        "game_versions": "[\"" + mc_version + "\"]"
    }
    res = requests.get(modrinth_api_url + "/project/" + mod + "/version", headers=headers, params=params)
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
        "modLoaderType": 4,
        "slug": mod
    }
    res = requests.get(curseforge_api_url + "/v1/mods/search", params=params, headers=headers)
    if res.status_code != 200:
        log(f"Failed to find {mod} on CurseForge")
        return None
    
    res = res.json()
    # iterate through results to find the correct mod
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
    candidates = [x for x in files if x["gameVersion"] == mc_version and x["modLoader"] == 4]
    fileId = candidates[mod_idx]["fileId"]
    filename = candidates[mod_idx]["filename"]

    # get download link from curseforge api
    res = requests.get(curseforge_api_url + f"/v1/mods/{modId}/files/{fileId}", headers=headers)
    if res.status_code != 200:
        log(f"Failed to fetch download URL for {mod} from CurseForge API")
        return None
    dl_link = res.json()["data"]["downloadUrl"]
    return dl_link, filename


# ugly, i know
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
    # remove existing mods
    clean_mods_dir()

    # read mod list
    mods = read_mod_list(mod_list)

    # iterate through mod list
    for i, mod in enumerate(mods):
        ticker = f"[{i+1}/{len(mods)}]"

        # order of requests: modrinth, curseforge, github
        # search until we find a mod, if we don't find it, skip it

        retval = get_from_modrinth(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            continue

        retval = get_from_curseforge(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            continue

        retval = get_from_github(mod)
        if retval is not None:
            dl_link, filename = retval
            dl_mod(dl_link, mod, filename)
            continue

        log(f"Failed to find {mod}, skipping...")


if __name__ == "__main__":
    main()
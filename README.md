# ModDownloader

This tool was initially made for personal use, since I use specific Fabric mods for Minecraft, but feel free to modify and use it for yourself.


## TODO

* Implement fuzzy searching instead of searching for exact matches


## Instructions

Adjust `mc_version`, `mod_list`, `mod_dir` and `mod_loader` variables in the [get_mods.py](get_mods.py) and run the script. Make sure you have Python 3 installed. You will also need to provide CurseForge API key for accessing CurseForge API and e-mail for accessing Modrinth API. You can get the key by registering on https://console.curseforge.com/ and requesting it there. For the e-mail, contact me on Discord.


## Why the hardcoded Github entries?

A couple of mods I use are only available on GitHub, which does provide an API, but you can't filter queries by Minecraft version and mod loader.


## Why didn't you just make a modpack?

I'd still probably have to manually update the modpack for every version.

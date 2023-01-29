# ModDownloader

ModDownloader is a Python 3 script that downloads mods for a specific Minecraft version for Fabric mod loader from Modrinth/CurseForge/Github into a specified directory. These parameters, along with path to your mod list file can be set inside the script.

This tool was initially made for personal use, since I use specific Fabric mods for Minecraft, but feel free to modify and use it for yourself.

For the future, I will probably make it mod loader invariant.

## Instructions

Adjust `mc_version`, `mod_list` and `mod_dir` variables in the [get_mods.py](get_mods.py) and run the script. Make sure you have Python 3 installed.

## Why the hardcoded Github entries?

A couple of mods I use are only available on GitHub, which does provide an API, but you can't filter queries by Minecraft version and mod loader.

## Why didn't you just make a modpack?

I don't know, gonna have to look into it.

# ModDownloader

ModDownloader is a Python 3 script that downloads mods for a specific Minecraft version for Fabric mod loader from CurseForge/Github into a specified directory. These parameters, along with path to your .minecraft directory can be set inside the script.

This tool was initially made for personal use, since I use specific Fabric mods for Minecraft, but feel free to modify and use it for yourself.

## Instructions

TODO

## What about Modrinth and why Github?

Some of the mods I use are available only on CurseForge, and some are available only on Github. On top of that, some mods also don't post releases on their GitHub repos. Modrinth, CurseForge and GitHub all provide APIs, and I ultimately decided for the CurseForge one, although the script could be easily modified to support searching for mods on all APIs at the same time. Modrinth and CurseForge APIs are also superior to the GitHub one since they offer filtering of files by Minecraft version and mod loader, which renders GitHub practically useless if the files don't have Minecraft version and mod loader info in their name. For the 3 mods from GitHub that I use, for now, I just made it so that you have to provide download links in the mod list file.

from pathlib import Path
import os
from os.path import isfile, isdir, join
from shutil import copytree, rmtree
import datetime
import time
import configparser
import json

###
# TODO add support for games that do not store saves within user directory
# TODO add creation of log file to allow user to monitor recent active of script
# TODO clean up imports
# TODO refactor code
# TODO test backing up to a NAS
###

if __name__ == '__main__':
    print("GameSaveCopy Started {}".format(datetime.datetime.now()))

    config = configparser.ConfigParser()
    config.read('config.ini')
    Preferences = config['Preferences']
    backupVersions = Preferences['NumberOfVersionsToKeep']
    backUpPath = Preferences['BackupDestination']

    Uplay = config['Uplay']
    UplayUserID = Uplay['UplayUserID']
    UplayClientLocation = Uplay['UplayClientLocation']

    Steam = config['Steam']
    options = config.options('Steam')
    steamAppsLocations = []
    for opt in options:
        # TODO Maybe update to use regex
        if (opt.find('steamapps') != -1):
            steamAppsLocations.append(Steam[opt][:Steam[opt].find('steamapps')]) if Steam[opt].find('steamapps') > -1 else steamAppsLocations.append(Steam[opt])

    with open("games.json", "r") as readFile:
        games = json.load(readFile)

    for game in games["games"]:
        relativeGamePath = game["path"]
        # TODO Maybe update to use regex
        if (relativeGamePath.find('Ubisoft Game Launcher') != -1):
            relativeGamePath = relativeGamePath.replace('<UplayUserID>', UplayUserID)
            if os.path.exists(join(UplayClientLocation[:UplayClientLocation.find('Ubisoft Game Launcher')], relativeGamePath)):
                absoluteGamePath = join(UplayClientLocation[:UplayClientLocation.find('Ubisoft Game Launcher')], relativeGamePath).replace("/", "\\")

        elif (relativeGamePath.find('Steam/userdata') != -1):
            relativeGamePath = relativeGamePath.replace('<SteamUserID>', Steam['SteamUserID'])
            if os.path.exists(join(Steam['SteamClientLocation'][:Steam['SteamClientLocation'].find('Steam')], relativeGamePath)):
                absoluteGamePath = join(Steam['SteamClientLocation'][:Steam['SteamClientLocation'].find('Steam')], relativeGamePath).replace("/", "\\")

        elif (relativeGamePath.find('steamapps') != -1):
            for steamApp in steamAppsLocations:
                if os.path.exists(join(steamApp, relativeGamePath)):
                    absoluteGamePath = join(steamApp, game["path"]).replace("/", "\\")

        else:
            absoluteGamePath = join(str(Path.home()), game["path"]).replace("/", "\\")
        gameName = game["name"]

        print("Current game: {}\nSave path: {}".format(gameName, absoluteGamePath))

        ###
        # Find the last time the game files were modified
        ###
        lastModGame = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)
        for root, dirs, files in os.walk(absoluteGamePath):
            for name in files:
                if (datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name))) > lastModGame):
                    lastModGame = datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name)))
            for name in dirs:
                if (datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name))) > lastModGame):
                    lastModGame = datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name)))

        ###
        # Find the last time the backup files were modified.
        ###
        lastModBackup = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)

        lastCreatedBackupDate = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)
        lastCreatedBackup = ""

        oldestCreatedBackup = datetime.datetime.today()
        backupToDelete = ""

        try:
            print("game to check for backups: {}".format(join(backUpPath, gameName)))
            backupDirectories = os.listdir(join(backUpPath, gameName))

            for backup in backupDirectories:
                ###
                # Find the last created backup to be searched to compare modification times with the current game saves.
                ###
                if (datetime.datetime.fromtimestamp(os.path.getctime(join(backUpPath, gameName, backup))) > lastCreatedBackupDate): lastCreatedBackup = join(backUpPath, gameName, backup)
                ###
                # Find the oldest backup if we have reached the user configured number of versions to keep.
                ###
                if (len(backupDirectories) == backupVersions):
                    if (datetime.datetime.fromtimestamp(os.path.getctime(join(backUpPath, gameName, backup))) < oldestCreatedBackup): backupToDelete = join(backUpPath, gameName, backup)
            ###
            # Find the most recent modification date of the most recent backup.
            ###
            for root, dirs, files in os.walk(lastCreatedBackup):
                for name in files:
                    if (datetime.datetime.fromtimestamp(os.path.getctime(join(root, name))) > lastModBackup):
                        lastModBackup = datetime.datetime.fromtimestamp(os.path.getctime(join(root, name)))
                for name in dirs:
                    if (datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name))) > lastModBackup):
                        lastModBackup = datetime.datetime.fromtimestamp(os.path.getctime(join(root, name)))
        except:
            print('Backups for {} do not exist, a new directory will be created.'.format(gameName))

        # Backup game files
        print("DEBUG: lastModGame: {}, lastModBackup: {}".format(lastModGame, lastModBackup))
        if lastModGame > lastModBackup:
            print("Starting backup of {} saves at {}.".format(gameName, datetime.datetime.now()))
            if not os.path.exists(join(backUpPath, gameName)):
                os.makedirs(join(backUpPath, gameName))
            copytree(absoluteGamePath, join(backUpPath, gameName, lastModGame.strftime("%Y-%m-%d %H.%M.%S")))
            print("Completed backup of {} saves at {}.".format(gameName, datetime.datetime.now()))
            if backupToDelete.strip():
                try:
                    print("Removing oldest backup version for {}.".format(gameName))
                    rmtree(backupToDelete)
                except:
                    print("Error: Failed to delete oldest backup {}.".format(backupToDelete))
        else:
            print("No changes to save for {} to backup.".format(gameName))
    print("GameSaveCopy Completed {}".format(datetime.datetime.now()))

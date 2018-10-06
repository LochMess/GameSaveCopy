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
###

if __name__ == '__main__':
    print("GameSaveCopy Started {}".format(datetime.datetime.now()))

    config = configparser.ConfigParser()
    config.read('config.ini')
    Preferences = config['Preferences']
    backupVersions = Preferences['NumberOfVersionsToKeep']
    backUpPath = Preferences['BackupDestination']

    with open("games.json", "r") as readFile:
        games = json.load(readFile)

    for game in games["games"]:
        gamePath = join(str(Path.home()), game["path"]).replace("/", "\\")
        gameName = game["name"]

        print("Current game: {}\nSave path: {}".format(gameName, gamePath))

        ###
        # Find the last time the game files were modified
        ###
        lastModGame = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)
        for root, dirs, files in os.walk(gamePath):
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
            print("Starting backup of {} saves.".format(gameName))
            if not os.path.exists(join(backUpPath, gameName)):
                os.makedirs(join(backUpPath, gameName))
            copytree(gamePath, join(backUpPath, gameName, lastModGame.strftime("%Y-%m-%d %H.%M.%S")))
            print("Completed backup of {} saves.".format(gameName))
            if backupToDelete.strip():
                try:
                    print("Removing oldest backup version for {}.".format(gameName))
                    rmtree(backupToDelete)
                except:
                    print("Error: Failed to delete oldest backup {}.".format(backupToDelete))
        else:
            print("No changes to save for {} to backup.".format(gameName))

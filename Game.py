import configparser
import os
from os.path import isfile, isdir, join
from pathlib import Path
import datetime
from shutil import copytree, rmtree

class Game:
    'Game object that represents game save locations.'
    config = configparser.ConfigParser()
    config.read('config.ini')
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


    def __init__(self, name, relPath):
        self.name = name
        self.relativePath = relPath.replace("/", "\\")
        # TODO maybe have setter property for path and read path and generate absolute path on instantiation of the object


    def isSavedInSteamApps(self):
        return True if self.relativePath.find('steamapps') != -1 else False


    def isSavedInUplay(self):
        return True if self.relativePath.find('Ubisoft Game Launcher') != -1 else False


    def isSavedInSteamUserdata(self):
        # TODO update to use regex or something to be more robust at handling foward/back slashes
        return True if self.relativePath.find('Steam/userdata') != -1 or self.relativePath.find('Steam\\userdata') != -1 else False


# TODO determine what logic to have in game and whether it should read the config file or have all it's info passed from the main file.
    def buildAbsoluteFilePath(self):
        if (self.isSavedInUplay()):
            self.relativePath = self.relativePath.replace('<UplayUserID>', Game.UplayUserID)
            path = join(Game.UplayClientLocation[:Game.UplayClientLocation.find('Ubisoft Game Launcher')], self.relativePath).replace("/", "\\")
            if os.path.exists(path):
                return path

        elif (self.isSavedInSteamUserdata()):
            self.relativePath = self.relativePath.replace('<SteamUserID>', Game.Steam['SteamUserID'])
            path = join(Game.Steam['SteamClientLocation'][:Game.Steam['SteamClientLocation'].find('Steam')], self.relativePath).replace("/", "\\")
            if os.path.exists(path):
                return path

        elif (self.isSavedInSteamApps()):
            for steamApp in Game.steamAppsLocations:
                path = join(steamApp, self.relativePath).replace("/", "\\")
                if os.path.exists(path):
                    return path
        else:
            return join(str(Path.home()), self.relativePath).replace("/", "\\")

        return '{} skipped game not installed.'.format(self.name)


    def getModificationDate(self, folderToSearch):
        mostRecentModification = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)
        errors = []
        for root, dirs, files in os.walk(folderToSearch, onerror=errors.append):
            for name in files:
                if (datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name))) > mostRecentModification):
                    mostRecentModification = datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name)))
            for name in dirs:
                if (datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name))) > mostRecentModification):
                    mostRecentModification = datetime.datetime.fromtimestamp(os.path.getmtime(join(root, name)))
        return mostRecentModification


    def countBackups(self, backupLocation):
        try:
            return int(len(os.listdir(join(backupLocation, self.name))))
        except:
            print('There are no backups for {} to count.'.format(self.name))


    def getBackupToDelete(self, backupLocation):
        oldestCreatedBackup = datetime.datetime.today()
        backupToDelete = ""

        try:
            # TODO same code as mostRecentBackupPath method look to merge same code into own function
            backupDirectories = os.listdir(join(backupLocation, self.name))

            for backup in backupDirectories:
                backupFolderPath = join(backupLocation, self.name, backup)
                if (datetime.datetime.fromtimestamp(os.path.getctime(backupFolderPath)) < oldestCreatedBackup):
                    backupToDelete = backupFolderPath
            return backupToDelete
        except:
            print('There are no backups for {} to delete.'.format(self.name))


    def mostRecentBackupPath(self, backupLocation):
        lastCreatedBackupDate = datetime.datetime(1901, 1, 1, 00, 00, 00, 00)
        lastCreatedBackup = ""

        try:
            backupDirectories = os.listdir(join(backupLocation, self.name))

            for backup in backupDirectories:
                backupFolderPath = join(backupLocation, self.name, backup)
                if (datetime.datetime.fromtimestamp(os.path.getctime(backupFolderPath)) > lastCreatedBackupDate):
                    lastCreatedBackup = backupFolderPath

            return self.getModificationDate(lastCreatedBackup)
        except:
            print('Backups for {} do not exist, a new directory will be created.'.format(self.name))


    def cleanOldBackups(self, backupLocation, backupVersionCount):
        if self.countBackups(backupLocation) > int(backupVersionCount):
            try:
                print("Removing oldest backup version for {}.".format(self.name))
                rmtree(self.getBackupToDelete(backupLocation))
            except:
                print("Error: Failed to delete oldest backup {}.".format(self.getBackupToDelete(backupLocation)))


    def backup(self, backupLocation):
        print("Starting backup of {} saves at {}.".format(self.name, datetime.datetime.now()))
        backupPath = join(backupLocation, self.name)
        saveAbsolutePath = self.buildAbsoluteFilePath()
        backupName = self.getModificationDate(saveAbsolutePath).strftime("%Y-%m-%d %H.%M.%S")
        if not os.path.exists(backupPath):
            os.makedirs(backupPath)
        copytree(saveAbsolutePath, join(backupPath, backupName))
        print("Completed backup of {} saves at {}.".format(self.name, datetime.datetime.now()))


    def __str__(self):
        return 'name: {}\nrelative file path: {}'.format(self.name, self.relativePath)

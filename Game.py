from os import walk, listdir, makedirs, remove
from os.path import join, exists, getmtime, getctime
from pathlib import Path
from datetime import datetime
from shutil import copytree, rmtree, make_archive
import logging
import re


class Game:
    'Game object that represents game save locations.'
    Uplay = None
    UplayUserID = None
    UplayClientLocation = None

    Steam = None
    SteamAppsLocations = None

    def __init__(self, name, relPath):
        self.name = name
        self.relativePath = relPath.replace("/", "\\")
        self.absolutePath = self.buildAbsoluteFilePath()
        self.installed = True if self.absolutePath and listdir(
            self.absolutePath) else False

    def isCompleteFilePath(self):
        return True if re.search('[A-Z]:{1}', self.relativePath) else False

    def isSavedInSteamApps(self):
        return True if self.relativePath.find('steamapps') != -1 else False

    def isSavedInUplay(self):
        return True if self.relativePath.find('Ubisoft Game Launcher') != -1 else False

    def isSavedInSteamUserdata(self):
        return True if self.relativePath.find('Steam/userdata') != -1 or self.relativePath.find('Steam\\userdata') != -1 else False

    def buildAbsoluteFilePath(self):
        if (self.isCompleteFilePath()):
            path = self.relativePath.replace("/", "\\")
            if exists(path):
                return path
        if (self.isSavedInUplay()):
            self.relativePath = self.relativePath.replace(
                '<UplayUserID>', Game.UplayUserID)
            path = join(Game.UplayClientLocation[:Game.UplayClientLocation.find(
                'Ubisoft Game Launcher')], self.relativePath).replace("/", "\\")
            if exists(path):
                return path

        elif (self.isSavedInSteamUserdata()):
            self.relativePath = self.relativePath.replace(
                '<SteamUserID>', Game.Steam['SteamUserID'])
            path = join(Game.Steam['SteamClientLocation'][:Game.Steam['SteamClientLocation'].find(
                'Steam')], self.relativePath).replace("/", "\\")
            if exists(path):
                return path

        elif (self.isSavedInSteamApps()):
            for steamApp in Game.SteamAppsLocations:
                path = join(steamApp, self.relativePath).replace("/", "\\")
                if exists(path):
                    return path
        else:
            path = join(str(Path.home()), self.relativePath).replace("/", "\\")
            if exists(path):
                return path
        logging.info('{} skipped game not installed.'.format(self.name))
        return None

    def hasNoBackups(self, backupLocation):
        mostRecentBackup = self.mostRecentBackupPath(backupLocation)
        modDateMostRecent = self.getModificationDate(
            join(backupLocation, self.name, mostRecentBackup))
        if not modDateMostRecent:
            return True
        return False

    def currentSaveBackedUp(self, backupPath):
        currentSave = self.getModificationDate(self.absolutePath)
        latestBackup = self.getModificationDate(
            join(backupPath, self.name, self.mostRecentBackupPath(backupPath)))
        if not currentSave or currentSave == latestBackup:
            return True
        return False

# TODO add compatibility for zip files?
    def getModificationDate(self, folderToSearch):
        if (folderToSearch == ""):
            return None
        mostRecentModification = datetime(1901, 1, 1, 00, 00, 00, 00)
        errors = []
        for root, dirs, files in walk(folderToSearch, onerror=errors.append):

            for name in files:
                if (datetime.fromtimestamp(getmtime(join(root, name))) > mostRecentModification):
                    mostRecentModification = datetime.fromtimestamp(
                        getmtime(join(root, name)))
            for name in dirs:
                if (datetime.fromtimestamp(getmtime(join(root, name))) > mostRecentModification):
                    mostRecentModification = datetime.fromtimestamp(
                        getmtime(join(root, name)))
        return mostRecentModification if not errors else None

    def countBackups(self, backupLocation):
        try:
            return int(len(listdir(join(backupLocation, self.name))))
        except:
            logging.info(
                'There are no backups for {} to count.'.format(self.name))

    def getBackupToDelete(self, backupLocation):
        oldestCreatedBackup = datetime.today()
        backupToDelete = ""

        try:
            backupDirectories = listdir(join(backupLocation, self.name))

            for backup in backupDirectories:
                backupFolderPath = join(backupLocation, self.name, backup)
                backupModificationTime = datetime.fromtimestamp(
                    getmtime(backupFolderPath))

                if (backupModificationTime < oldestCreatedBackup):
                    backupToDelete = backupFolderPath
                    oldestCreatedBackup = backupModificationTime

            return backupToDelete
        except:
            logging.info(
                'There are no backups for {} to delete.'.format(self.name))

# TODO shouldn't be a function on the game object
    def stripZipExtensionFromString(self, fileName):
        return fileName[:fileName.find('.zip')]

# TODO shouldn't be a function on the game object
    def isZipFile(self, fileName):
        return fileName.find('.zip') != -1

    def mostRecentBackupPath(self, backupLocation):
        dateCursor = datetime(1901, 1, 1, 00, 00, 00, 00)
        mostRecentBackup = ""

        try:
            for file in listdir(join(backupLocation, self.name)):
                dateString = file
                if (self.isZipFile(file)):
                    dateString = self.stripZipExtensionFromString(file)
                try:
                    dateFromString = datetime.strptime(
                        dateString, "%Y-%m-%d %H.%M.%S")
                    if (dateFromString > dateCursor):
                        mostRecentBackup = file
                        dateCursor = dateFromString
                except:
                    logging.info(
                        "Filename '{}' is not a date matching the expected format.".format(file))

            return mostRecentBackup
        except:
            logging.info(
                'Backups for {} do not exist, a new directory will be created.'.format(self.name))
            return ""

    def cleanOldBackups(self, backupLocation, backupVersionCount):
        if self.countBackups(backupLocation) > int(backupVersionCount):
            try:
                logging.info(
                    "Removing oldest backup version for {}.".format(self.name))
                versionToDelete = self.getBackupToDelete(backupLocation)

                if versionToDelete.find('.zip'):
                    remove(versionToDelete)
                else:
                    rmtree(versionToDelete)
            except:
                logging.warning("Error: Failed to delete oldest backup {}.".format(
                    self.getBackupToDelete(backupLocation)))

    def backup(self, backupLocation):
        logging.info("Starting backup of {} saves at {}.".format(
            self.name, datetime.now()))
        backupPath = join(backupLocation, self.name)
        backupName = self.getModificationDate(
            self.absolutePath).strftime("%Y-%m-%d %H.%M.%S")
        if not exists(backupPath):
            makedirs(backupPath)
        copytree(self.absolutePath, join(backupPath, backupName))
        logging.info("Completed backup of {} saves at {}.".format(
            self.name, datetime.now()))

    def compress(self, backupLocation):
        backupPath = join(backupLocation, self.name)
        backups = list(filter(lambda file: file.find(
            '.zip') == -1, listdir(backupPath)))
        if len(backups) > 1:
            logging.info("Compressing previous backups.")
            for backup in backups[:-1]:
                currentBackupPath = join(backupPath, backup)
                make_archive(currentBackupPath, 'zip', currentBackupPath)
                logging.info(
                    "Removing uncompressed previous backup {}.".format(backup))
                rmtree(currentBackupPath)

    def __str__(self):
        return 'name: {}\nrelative file path: {}'.format(self.name, self.relativePath)

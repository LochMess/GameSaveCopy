from datetime import datetime
import configparser
import json
import logging
from Game import Game

# Imports for logs clean up
from os import remove, listdir, path, makedirs
from os.path import realpath, join, exists

###
# TODO Make logging cleaner... seperate class?
# TODO refactor code
# TODO look at compressing backups maybe not the current one just the previous versions?
# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
# potential issue with compression, making new zip files means new creation times for the files, solution compress oldest first
# TODO allow the games.json file to contain absolute file paths
###
def configureLogging():
    logging.basicConfig(
        filename = 'logs/GameSaveCopy {}.log'.format(datetime.now().strftime("%Y-%m-%d %H.%M.%S")),
        format = '%(levelname)s: %(message)s',
        filemode = 'w',
        level = logging.INFO
    )

def deleteOldLogs(numberOfLogsToKeep, logsPath):
    logFiles = listdir(logsPath)
    if len(logFiles) > numberOfLogsToKeep:
        logging.info("Removing old log files.")
        for file in logFiles[:-numberOfLogsToKeep]:
            remove(join(logsPath, file))

if __name__ == '__main__':
    logsPath = realpath(__file__)[:realpath(__file__).rfind('\\')] + '\\logs\\'
    if not exists(logsPath):
        makedirs(logsPath)

    configureLogging()

    logging.info("GameSaveCopy Started {}".format(datetime.now()))

    config = configparser.ConfigParser()
    config.read('config.ini')
    Preferences = config['Preferences']
    backupVersions = Preferences['NumberOfVersionsToKeep']
    backUpPath = Preferences['BackupDestination']
    logsToKeep = int(Preferences['LogsToKeep'])

    Game.Uplay = config['Uplay']
    Game.UplayUserID = Game.Uplay['UplayUserID']
    Game.UplayClientLocation = Game.Uplay['UplayClientLocation']

    Game.Steam = config['Steam']
    options = config.options('Steam')
    steamAppsLocations = []

    for opt in options:
        # TODO Maybe update to use regex
        if (opt.find('steamapps') != -1):
            steamAppsLocations.append(Game.Steam[opt][:Game.Steam[opt].find('steamapps')]) if Game.Steam[opt].find('steamapps') > -1 else steamAppsLocations.append(Game.Steam[opt])

    Game.SteamAppsLocations = steamAppsLocations

    with open("games.json", "r") as readFile:
        games = json.load(readFile)

    for game in games["games"]:

        gameObj = Game(game["name"], game["path"])

        if not gameObj.mostRecentBackupPath(backUpPath) or gameObj.getModificationDate(gameObj.buildAbsoluteFilePath()) > gameObj.mostRecentBackupPath(backUpPath):
            gameObj.backup(backUpPath)
            gameObj.cleanOldBackups(backUpPath, backupVersions)
        else:
            logging.info("No changes to save for {} to backup.".format(gameObj.name))

    deleteOldLogs(logsToKeep, logsPath)

    logging.info("GameSaveCopy Completed {}".format(datetime.now()))

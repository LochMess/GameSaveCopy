from datetime import datetime
import configparser
import json
import logging
from Game import Game

from os import remove, listdir, path, makedirs
from os.path import realpath, join, exists


def configureLogging(logsPath):
    logging.basicConfig(
        filename=join(logsPath, 'GameSaveCopy {}.log'.format(
            datetime.now().strftime("%Y-%m-%d %H.%M.%S"))),
        format='%(levelname)s: %(message)s',
        filemode='w',
        level=logging.INFO
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

    configureLogging(logsPath)

    logging.info("GameSaveCopy Started {}".format(datetime.now()))

    config = configparser.ConfigParser()
    config.read('config.ini')
    Preferences = config['Preferences']
    backupVersions = Preferences['NumberOfVersionsToKeep']
    backUpPath = Preferences['BackupDestination']

    logsToKeep = int(Preferences['LogsToKeep'])

    compress = Preferences['Compress']

    Game.Uplay = config['Uplay']
    Game.UplayUserID = Game.Uplay['UplayUserID']
    Game.UplayClientLocation = Game.Uplay['UplayClientLocation']

    Game.Steam = config['Steam']
    options = config.options('Steam')
    steamAppsLocations = []

    for opt in options:
        if (opt.find('steamapps') != -1):
            steamAppsLocations.append(Game.Steam[opt][:Game.Steam[opt].find('steamapps')]) if Game.Steam[opt].find(
                'steamapps') > -1 else steamAppsLocations.append(Game.Steam[opt])

    Game.SteamAppsLocations = steamAppsLocations

    with open("games.json", "r") as readFile:
        games = json.load(readFile)

    for game in games["games"]:

        gameObj = Game(game["name"], game["path"])

        if gameObj.installed:

            if gameObj.hasNoBackups(backUpPath) or not gameObj.currentSaveBackedUp(backUpPath):
                gameObj.backup(backUpPath)
                gameObj.cleanOldBackups(backUpPath, backupVersions)
            else:
                logging.info("No changes to save for {} to backup.".format(gameObj.name))

            if compress.lower().find('true') or compress.lower().find('yes'):
                gameObj.compress(backUpPath)

    deleteOldLogs(logsToKeep, logsPath)

    logging.info("GameSaveCopy Completed {}".format(datetime.now()))
from datetime import datetime
import configparser
import json
from Game import Game

###
# TODO add support for games that do not store saves within user directory
# TODO add creation of log file to allow user to monitor recent active of script
# https://docs.python.org/2/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html
# TODO clean up imports
# TODO refactor code
# TODO test backing up to a NAS
# TODO look at compressing backups maybe not the current one just the previous versions?
# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
###

if __name__ == '__main__':
    print("GameSaveCopy Started {}".format(datetime.now()))

    config = configparser.ConfigParser()
    config.read('config.ini')
    Preferences = config['Preferences']
    backupVersions = Preferences['NumberOfVersionsToKeep']
    backUpPath = Preferences['BackupDestination']

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

    print('Type config: {}, preferences: {}'.format(type(config), type(Preferences)))

    with open("games.json", "r") as readFile:
        games = json.load(readFile)

    for game in games["games"]:

        gameObj = Game(game["name"], game["path"])

        # print("Game backup modification time: {}".format(gameObj.getModificationDate(gameObj.mostRecentBackupPath(backUpPath))))
        # print('abso path: {}, most recent path: {}'.format(gameObj.buildAbsoluteFilePath(), gameObj.mostRecentBackupPath(backUpPath)))
        if not gameObj.mostRecentBackupPath(backUpPath) or gameObj.getModificationDate(gameObj.buildAbsoluteFilePath()) > gameObj.mostRecentBackupPath(backUpPath):
            gameObj.backup(backUpPath)
            gameObj.cleanOldBackups(backUpPath, backupVersions)
        else:
            print("No changes to save for {} to backup.".format(gameObj.name))

        # print('gameObj: {}, steamapps: {}, uplay: {}, steam userdata: {}, gameOBj absolute path: {}'.format(gameObj, gameObj.isSavedInSteamApps(), gameObj.isSavedInUplay(), gameObj.isSavedInSteamUserdata(), gameObj.buildAbsoluteFilePath()))

    print("GameSaveCopy Completed {}".format(datetime.now()))

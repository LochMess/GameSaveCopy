# Game Save Copy
Python script to copy game saves to a user specified directory and keep a user specified number of versions of said game save backups.

## Setup and Configuration ##
### Configure the config.ini ###
1. **config.ini** rename the 'TEMPLATE config.ini' file to 'config.ini' and follow the below steps to configure the script to run how you would like it too.
2. **Preferences**
    **BackupDestination**: Where you want your saves to be backed up to ie `C:\Users\Fred\Desktop\Game Save Backups`</br>
    **NumberOfVersionsToKeep**: How many versions to keep of your saves, GameSaveCopy only created a new backup when it executes and there is an update file within the game save location, previous backups are automatically deleted when this number is exceeded. Takes a positive integer ie `3`</br>
    **LogsToKeep**: When GameSaveCopy executes it produces log files, the value you give here determines how many log files total to keep at any one time. For example if you want to have logs from the last 5 executions set this to `5`</br>
    **Compress**: Determines whether to compress your previous versions or not. It does not compress your latest backup version. Not case sensitive possible values `True`, `yes`, `false`, `no`</br>
3. **Steam**</br>
    **SteamUserID**: Steam user ID, used for building absolute file paths to game saves.</br>
    **SteamClientLocation**: Path of your steam client install ie `C:\Program Files (x86)\Steam`</br>
    **SteamApps1**: Location of one of your steamapps folders for example `C:\Program Files (x86)\Steam\steamapps`</br>
    **SteamApps2**: Location of another steamapps folder if you have more than one. This 'SteamApps' field can be repeated as many times as need just increment the integer at the end.</br>
4. **Uplay**  
    **UplayUserID**: Uplay user ID, used for building absolute file paths to game saves.</br>
    **UplayClientLocation**: Path of your uplay client install ie `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher`

### Add more games ###
The 'games.json' file is where the name and absolute or relative path to a game's saves are stored, to add aditional games simply follow the existing structure of the file below are examples of how you could add a new game using a relative path or absolute path.
Relative path:
```
{
    "name": "Mafia 3",
    "path": "C:/Users/Fred/AppData/Local/2K Games/Mafia III"
},
```
Absolute path:
```
{
    "name": "Mafia 3",
    "path": "AppData/Local/2K Games/Mafia III"
},
```

### (Optional) Schedule the execution of the script ###
1. Go to `Control Panel > Administrative Tools > Task Scheduler`</br>
or search for `Task Scheduler` in the start menu.
2. Select `Create Basic Task`
3. Complete the wizard naming your scheduled task, selecting the trigger to your desired schedule ie daily at 5:30pm.
    * For the action section of the wizard select `Start a program`
    * For the 'Program/script' field enter the location of the python.exe installed on your system to check this open a powershell or cmd and run the following.
    ```
    python
    import sys
    sys.executable
    ```
    * For 'Add arguments (optional)' enter `main.py`
    * For 'Start in (optinal)' enter the path to the directory main.py is within ie `C:\Users\Fred\CodeStuff\GameSaveCopy\`
8. Complete the wizard and GameSaveCopy should run on the schedule you just configured.
3. Test the scheduled task you just created, select it from the list and select run from the right of the screen then check your backup location for your save backups and your GameSaveCopy location for the logs from the execution of the script.

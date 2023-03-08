# Dev utils

## Copy addon files to Anki addons folder

### Windows
```bat
xcopy /y src\* C:\Users\[user]\AppData\Roaming\Anki2\addons21\nal-dev
```

or

```bat
xcopy /y src\* %AppData%\Anki2\addons21\nal-dev
```

### Linux

```bash
clear & cp src/* /home/[user]/.local/share/Anki2/addons21/1894428367dev & anki | grep ^NAL
```

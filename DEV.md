# Dev utils

## Copy addon files to Anki addons folder

### Windows
```bat
xcopy /y * C:\Users\[user]\AppData\Roaming\Anki2\addons21\nal-dev
```

or

```bat
xcopy /y * %AppData%\Anki2\addons21\nal-dev
```

### Linux

```bash
clear & cp * /home/[user]/.local/share/Anki2/addons21/1894428367dev & anki | grep ^NAL
```

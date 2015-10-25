Bottle decorators:

    http://stackoverflow.com/a/8620964

## MongoDB commands

    show databases

## Mongodb on Mac OSX

To have launchd start mongodb at login:
    
    ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents

Then to load mongodb now:

    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist

Or, if you don't want/need launchctl, you can just run:

    mongod --config /usr/local/etc/mongod.conf
    

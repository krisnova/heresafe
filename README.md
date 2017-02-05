# heresafe
Text someone once you connect to a WiFi network.

With heresafe you can easily configure your Mac to send an SMS message via Google Voice upon connecting to a specified wireless network.

Inspiration for heresafe came from my inability to remember to text my partner when I am safely at the office each day.

# Installing

You **must** have a valid Google Voice account. After you have created one at [voice.google.com](https://voice.google.com) you can proceed to follow the following installation steps:
 
```
pip install heresafe
heresafe configure
```

# heresafe configure

Will query the user for input parameters to run heresafe

# heresafe check

Will actually run a check for heresafe, and see if a text needs to be sent.

# How it works

### Google Voice

We use Google Voice to send a text message via their API from a registered Google voice number.

### Crontab

We use your users crontab to keep things friendly. By design heresafe will never ask for sudo, and will only run for your user's crontab.

### Internal store

#### ~/.heresafe/config

The heresafe configuration file. This can be edited directly, or using `heresafe configure`

#### ~/.heresafe/last

The timestamp of the last text message sent with heresafe

#### ~/.heresafe/crontab

The crontab that heresafe is using.

#### ~/.heresafe/log

If verbose is enabled, the log directory for all heresafe output.

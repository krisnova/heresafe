# heresafe
Text someone once you connect to a WiFi network.

With heresafe you can easily configure your Mac to send an SMS message via Google Voice upon connecting to a specified wireless network.

Inspiration for heresafe came from my inability to remember to text my partner when I am safely at the office each day.

# Installing

You **must** have a valid Google Voice account. After you have created one at [voice.google.com](https://voice.google.com) you can proceed to follow the following installation steps:
 
```bash
pip install heresafe
heresafe configure
```

```
kris-nova:heresafe kris$ heresafe configure
heresafe 1.0.2:  In order to use heresafe, you must have a valid Google voice account.
Google Voice Email [kris@nivenly.com]: 
Google Voice Password [*]: 
Send Message To # [+13038675309]: 
Send Message Body [*]: Hey baby, Just got to work safe. I love you!
Send Once Per (day|nday|hour|nhour)[day]: 
Send Once You Connect to SSID [office-wifi]:
heresafe 1.0.2:  Writing config to filesystem
How often should we check? (in minutes) [15]: 
heresafe 1.0.2:  Configuring crontab
heresafe 1.0.2:  Configuration complete!
heresafe 1.0.2:  Modified your crontab. You can edit it with crontab -e, or remove it with crontab -r
heresafe 1.0.2:  All configuration for heresafe is stored in PLAINTEXT in ~/.heresafe
heresafe 1.0.2:  Bye!
kris-nova:heresafe kris$ 
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

#!/usr/bin/python
########################################################################################################################
#
# Copyright 2017 Kris Nova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
########################################################################################################################

import sys
import os
import readline
from subprocess import Popen, PIPE
from googlevoice import Voice
import datetime
import ConfigParser
import subprocess

# Execution Parameters
version = "1.0.3"
verbose = True  # Will echo log lines to standard out
log = False  # Will write logs to log file
show_errors = True
logdate_format = "%Y-%m-%d %H:%M"

# Configuration
send_to_number = ""
send_once_per = "day"  # Available options are: "day" "Xday" "hour" "Xhour"
send_message = "Canary message from heresafe %s. Written by Kris Nova. Apache Licensed Copyright 2017." % (version)
send_on_ssid = ""

google_voice_email = "user@gmail.com"
google_voice_pass = "password"

seriously_actually_send_the_text = True

# Usage for the tool
description = '''
\033[1mheresafe\033[0m V%s

Author: Kris Nova <kris@nivenly.com>

    Quick Start : heresafe configure

    \033[1mheresafe\033[0m is a Python utility that will send an arbitrary text message to a configured number when a script runs and detects you are connected to a certain SSID.
    This tool is catered to work on OSX. Any other operating systems are currently not supported.

    The inspiration for the tool was solely inspired by the love of my partner, and my desire to let her know I am always safe and sound whenever I arrive at work each morning.

[ACTIONS]

    \033[95m[configure]\033[0m Will configure heresafe to run on your system.
        heresafe configure

    \033[95m[check]\033[0m Will run heresafe, and check if you there safe! Will send a text if needed.
        heresafe check

''' % version

plist = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>heresafe</key>
        <string>com.heresafe.heresafe.heresafe</string>
        <key>ProgramArguments</key>
        <array>
            <string>heresafe check</string>
        </array>
        <key>StartInterval</key>
        <integer>{SECONDS}</integer>
    </dict>
</plist>
'''

# Fix the GNU vs BSD tab completion problem
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


def main():
    '''
    heresafe is a Python utility that will send an arbitrary text message to a configured number when a script runs and detects you are connected to a certain SSID.
    '''
    try:
        firstarg = sys.argv[1]
        if firstarg == "-h" or firstarg == "--help":
            sys.exit(1)
    except:
        print description
        sys.exit(1)

    ensure_datastore()
    if firstarg == "":
        heresafe()
    try:
        action_function = 'action_' + firstarg
        if firstarg == "configure":
            action_configure()
        elif firstarg == "check":
            action_check()
        else:
            f = getattr(sys.modules[__name__], action_function)
            f(sys.argv[2])
    except SystemExit:
        out("Exiting..")
        sys.exit(1)
    except KeyboardInterrupt:
        out("\nSIGTERM detected. Exiting gracefully")
    except IndexError:
        if show_errors:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        print description
        sys.exit(1)
    except AttributeError:
        if show_errors:
            print sys.exc_info()
    except:
        if show_errors:
            print sys.exc_info()
    out("Bye!")


def action_configure():
    '''

    Will configure heresafe to run on your system.
    '''
    load_config()
    config = ConfigParser.ConfigParser()
    out("In order to use heresafe, you must have a valid Google voice account.")
    config.add_section('voice')
    # Google Voice Email
    raw_email = raw_input("Google Voice Email [%s]: " % google_voice_email)
    if raw_email == "":
        config.set("voice", "email", google_voice_email)
    else:
        config.set("voice", "email", raw_email)

    # Google Voice Password
    raw_pass = raw_input("Google Voice Password [*]: ")
    if raw_pass == "":
        config.set("voice", "password", google_voice_pass)
    else:
        config.set("voice", "password", raw_pass)

    config.add_section('heresafe')
    # Send Message Number
    raw_to = raw_input("Send Message To # [%s]: " % send_to_number)
    if raw_to == "":
        config.set("heresafe", "send_to_number", send_to_number)
    else:
        # Fix for the lazy Americans
        if "+1" not in raw_to:
            raw_to = "+1" + raw_to
        config.set("heresafe", "send_to_number", raw_to)

    # Send Message Body
    raw_msg = raw_input("Send Message Body [*]: ")
    if raw_msg == "":
        config.set("heresafe", "send_message", send_message)
    else:
        config.set("heresafe", "send_message", raw_msg)

    # Send Once Per
    raw_per = raw_input("Send Once Per (day|nday|hour|nhour)[%s]: " % send_once_per)
    if "day" not in raw_per and "hour" not in raw_per and raw_per != "":
        # Only try once
        out("Must select day, hour, nday, nhour")
        raw_per = raw_input("Send Once Per (day|nday|hour|nhour)[%s]: " % send_once_per)
    if raw_per == "":
        config.set("heresafe", "send_once_per", send_once_per)
    else:
        config.set("heresafe", "send_once_per", raw_per)

    # Send on SSID
    raw_ssid = raw_input("Send Once You Connect to SSID [%s]: " % send_on_ssid)
    if raw_ssid == "":
        config.set("heresafe", "send_on_ssid", send_on_ssid)
    else:
        config.set("heresafe", "send_on_ssid", raw_ssid)

    out("Writing config to filesystem")
    cfgfile = open(os.path.expanduser('~') + "/.heresafe/config", 'w')
    config.write(cfgfile)

    raw_check_duration = raw_input("How often should we check? (in minutes) [15]: ")
    if raw_check_duration == "":
        raw_check_duration = "15"

    out("Configuring crontab")
    cron_line = "*/%s * * * * heresafe check \n" % raw_check_duration
    # Easy debugging for crontab just in case ;)
    #cron_line = "*/%s * * * * heresafe check >> ~/.heresafe/log 2>&1\n" % raw_check_duration

    try:
        existing = subprocess.check_output("crontab -l", shell=True)
    except subprocess.CalledProcessError:
        # No existing crontab
        existing = ""

    lines = existing.split("\n")
    new = ""
    for line in lines:
        lineToWrite = line
        if "heresafe check" in line:
            lineToWrite = cron_line
        new += lineToWrite + "\n"
    if existing == "" or existing == "\n":
        new = 'MAILTO=""\n' + "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n\n" + cron_line

    last = open(os.path.expanduser('~') + "/.heresafe/crontab", "w")
    last.write(new)
    last.close()

    os.system('cat ~/.heresafe/crontab | crontab')

    out("Configuration complete!")
    out("Modified your crontab. You can edit it with crontab -e, or remove it with crontab -r")
    out("All configuration for heresafe is stored in PLAINTEXT in ~/.heresafe")


def load_config():
    cfg = get_raw_config()
    if cfg == "":
        return
    global send_message, send_once_per, send_to_number, send_on_ssid, google_voice_email, google_voice_pass
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~') + "/.heresafe/config")
    send_message = config.get("heresafe", "send_message")
    send_once_per = config.get("heresafe", "send_once_per")
    send_to_number = config.get("heresafe", "send_to_number")
    send_on_ssid = config.get("heresafe", "send_on_ssid").lower()
    google_voice_pass = config.get("voice", "password")
    google_voice_email = config.get("voice", "email")


def action_check():
    '''

    Will check if you are somewhere safe, and send a text if needed.
    '''
    load_config()

    # Get SSID
    ssid = get_ssid()
    if ssid == "":
        out("Hrmm.. Missing SSID. Not connected, or problem with airport.")
        return
    out("Hrmm.. It looks like you are connected to the SSID " + ssid)

    # Check if are on the right SSID
    if ssid != send_on_ssid.lower():
        out("Okay.. It looks like you aren't connected to SSID " + send_on_ssid)
        return
    out("Okay.. So you are connected to SSID " + ssid + ". You probably are somewhere safe!")

    last = get_last()

    if send_once_per == "day":
        sinceline = "a day"
        notify_after = datetime.datetime.now() - datetime.timedelta(days=1)
    elif "day" in send_once_per:
        n = send_once_per.replace("day", "")
        sinceline = n + " day(s)"
        notify_after = datetime.datetime.now() - datetime.timedelta(days=int(n))
    elif send_once_per == "hour":
        sinceline = "an hour"
        notify_after = datetime.datetime.now() - datetime.timedelta(hours=-1)
    elif "hour" in send_once_per:
        n = send_once_per.replace("hour", "")
        sinceline = n + " hour(s)"
        notify_after = datetime.datetime.now() - datetime.timedelta(hours=int(n) * -1)
    else:
        out(
            "And.. I don't seem to understand how often you want to send a text with your configuration: " + send_once_per)
        return

    if last != "" and last != "\n":
        last_time = datetime.datetime.strptime(last, logdate_format).date()
        # out("Notify after : "+ notify_after.date().strftime(logdate_format))
        # out("Last time    : "+ last_time.strftime(logdate_format))
        if last_time >= notify_after.date():
            out(
                "And.. it looks like heresafe already texted someone within " + sinceline + " ago.. I shouldn't do anything")
            return

    out("And.. It looks like heresafe hasn't texted since at least " + sinceline + " ago.. I better send a text")
    send_text()


def send_text():
    # Log in with Google voice
    voice = Voice()
    out("Now.. just logging in as " + google_voice_email + " really quick..")
    voice.login(email=google_voice_email, passwd=google_voice_pass)

    # Send text
    if seriously_actually_send_the_text:
        voice.send_sms(send_to_number, send_message)

    # Log
    ts = datetime.datetime.now().strftime(logdate_format)
    out("Alright.. I sent a text to " + send_to_number + " at " + ts)

    # Update our last message sent
    last = open(os.path.expanduser('~') + "/.heresafe/last", "w")
    last.write(ts)
    last.close()


def get_last():
    with open(os.path.expanduser('~') + "/.heresafe/last") as f:
        return f.read()


def get_raw_config():
    with open(os.path.expanduser('~') + "/.heresafe/config") as f:
        return f.read()


def get_ssid():
    '''
    Use the Mac OSx on board airport tool to check out what the user is connected to via airport.
    '''
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    p = Popen([airport, '-I'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    wifi, err = p.communicate()
    rc = p.returncode
    if rc != 0:
        # Todo we can probably handle these errors better
        return ""

    lines = wifi.split("\n")
    for line in lines:
        lowerline = line.lower()
        if "ssid" in lowerline and "bssid" not in lowerline:
            spl = lowerline.split(":")
            if len(spl) > 1:
                return spl[1].strip()

    return ""


def ensure_datastore():
    '''
    Will ensure a directory exists ~/.heresafe
    Will ensure there is a file ~/.heresafe/data has been created
    Will ensure there is a file ~/.heresafe/log has been created
    Will ensure there is a file ~/.heresafe/config has been created
    '''
    if not os.path.exists(os.path.expanduser('~') + "/.heresafe"):
        print "Setting up heresafe datastore: ~/.heresafe"
        os.makedirs(os.path.expanduser('~') + "/.heresafe")
    if not os.path.exists(os.path.expanduser('~') + "/.heresafe/last"):
        f = open(os.path.expanduser('~') + "/.heresafe/last", 'w')
        f.write("")
        f.close()
    if not os.path.exists(os.path.expanduser('~') + "/.heresafe/config"):
        f = open(os.path.expanduser('~') + "/.heresafe/config", 'w')
        f.write("")
        f.close()
    if not os.path.exists(os.path.expanduser('~') + "/.heresafe/log"):
        f = open(os.path.expanduser('~') + "/.heresafe/log", 'w')
        f.write("")
        f.close()


def out(message):
    withcolor = "\033[1hheresafe %s: \033[0m \033[95m%s\033[0m" % (version, message)
    with open(os.path.expanduser('~') + "/.heresafe/log", 'a') as log:
        log.write(message + "\n")
    if verbose:
        print withcolor

# Botstrap the program
if __name__ == "__main__":
    main()

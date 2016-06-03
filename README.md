## Release notes version 1.1.0: ##
* **IMPORTANT: Database updates required:** To use version 1.1.0 the config table has to be recreated and the stored config data will be lost and has to be reentered. Septs:
    1. Write down your settings somewhere
    2. Download new version
    3. Run *Doberman.py -n*
    4. Confirm to recreate *config_history*, *alarm_history* and *config*
    5. Deny to recreate *contacts*
    6. Run *Doberman.py -a* to reenter the settings (for all plugins)
 

* **Rename:** The software was baptized "Doberman". It can now be started over *Doberman.py [-opts]*.

* **Database changes:** Database changes can now also be entered over the main program *Doberman.py -opts* or as before with the database script (*DobermanDB.py -opts*). There are two types of config updates: *-u* askes to update only parameters which are often changed (Status, alarm status and all warning/alarm limits). *-uu* asks to update all config parameters.

* **Addidtional parameters:** The config has a new column *Additional parameters* where anything can be entered and sent to the plugin as .opts.additional_parameters (String format)

* **Recurrence Counter:** New a alarm recurrence counter exists. A value can be set for each plugin and each datachannel. An alarm or warning will only be sent, if the recurrence counter reaches the set paramter (default = 1). If a incoming data is not ok the counter is increased by one (independed whether the data value is out of the alarm/warning limit, the status is not ok, no connection to the device or the time difference since the last measurement is to big). A measurement which is ok decreases the counter by one, until it is back to 0.

* **Alarm history:** An alarm history logs all outgoing alarms. Alarms are only logged if the reccurence limit was reached.

* **Warning/Alarm Emails:** Warning and alarm emails provide more informations now (General settings, plugin settings, latest data and status, latest alarms).

# Doberman: Slow Control Monitoring #

**Author: P. Zappa **

Date: 16. June 2015

## Brief ##

The programs are made for a slow control of a system with several controllers (e.g. permanent observation of temperature, pressure and other quantities of an experiment). The main program (Doberman.py) is programmed generically so that it is independant of the used controllers. All controllers given in the settings are started with their individual program (can also be written in an other programming language), and have to transfer their data back to the main program. The collected data is then stored in a database, and can be monitored.

See darkwiki for further infos: http://www.lhep.unibe.ch/darkmatter/darkwiki/doku.php?id=local:labtpc:slow_control

## Prerequisites ##

The code is designed for python2.7 on linux. The computer should be compatible with all individual programs which are imported by the main Doberman slow control program. Also a PostgreSLQ database is advised.

## Installation ##

Download this repository to a directory. Install python and required packages by runing e.g. 'pip install -r requirements.txt' throung the terminal.
Also install PostgreSLQ (Tutorial: http://www.postgresql.org/docs/9.2/static/tutorial-install.html), create a database (Tutorial: http://www.postgresql.org/docs/9.2/static/tutorial-createdb.html) and write the connection details in the file '*Database_connectiondetails.txt*'. To create the tables in the database run '*DobermanDB.py -n*' in the terminal. Fill out the files '*MAIL_connectiondetails.txt*' and '*SMS_connectiondetails.txt*' for the warning and alarm sending.


## Usage ##

### Run main program ###
Navigate to your Doberman slow control folder and run in the terminal the '*Doberman.py [-opts]*' script.

The different options '*-opt*' are:

* -t[=x]: test modus: no alarms will be sent [for the first x minutes] (default t=2 minutes).

* -d=x: log level: what messages get to the terminal (x=10: debug (default),x=20: info, x=30: warning, x=40: error, x=50: critical)

* -i=x: import timeout: how long to wait for each controller (x in seconds). (default i=10 s)

* -o=x[,y,]: occupied ttyUSB ports: Use this option if the Doberman slow control should not connect to a [several] ttyUSB port x [and y,...]. This can be usefull if you dont want to disturb a controller which is already connected.

* -wr: warning repetition: minimum time after a warning or alarm until a new warning can be sent.

* -ar: alarm repetition: minimal time after an alarm befor a new alarm can be sent.

### Add a controller to the settings ###
Run '*DobermanDB.py -a*' in the terminal. Also make sure you follow the steps on darkwiki (http://www.lhep.unibe.ch/darkmatter/darkwiki/doku.php?id=local:labtpc:slow_control) on how to properly write the controller specific code and where to save it.
### Change/update controller settings ###
Run '*DobermanDB.py -u*' in the terminal to update status, alarm status and all alarm/warning limits
Run '*DobermanDB.py -u*' in the terminal to update all config parameters
### Manage contatacts for alarm/warning distribution ###
Run '*DobermanDB.py -c*' in the terminal.
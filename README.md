# SafeScan

<p><img src="https://github.com/Bot-JohnLemon/SafeScan/assets/28149894/049baa99-aca0-4ec0-b141-951003ba5b82" width="300" height="400" align="right"></p>

SecureScan is an advanced antivirus project that leverages report management through the use of the `VirusTotal API`.

This sophisticated software is designed to meticulously curate and administer files for in-depth analysis, with the resultant data being securely stored within a user-centric database.

Please note that this current iteration serves as an initial blueprint and will undergo a series of progressive enhancements within this repository, culminating in its ultimate and perfected version.

<br>

## Pre-installation

>Please follow the next steps to have a funcitional version of SafeScan software.

<br>

The first thing you have to do is to install `Python v.3` software to be able to run the program, also you have to install the next extensions for python too:

```sh
pip install mysql.connector
pip install requests
pip install urllib.parse
pip install time
```

<br>
 
The last thing is to have the software of `MySQL` fully installed and configured, note that the specs of the user and password could be changed in the code to adapt it to yourself on line 12 and 13:

```sh
"user": "root"       ----->   "user": "your_user"
"password": "1234"   ----->   "password": "your_passwd"
```

# How it works:

- First run the software, you will see that it asks you if you have a premium version (but its not implemented for now).

- After that you can see that it asks you for a specific path for the analysis print it on the prompt.

- The program will analize all the files that are in that folder.
  <br><br><br>

# -surl-
A tool that inspects all incoming packets and filters them by ``` destination port ```

For the url requests it works with:
  * GET requests only (for now)
  * an ip manager which blocks connections to every host that tries to flood your webserver [ http flood ]

For ssh it:
  * checks the /var/log/auth.log file to see if there are any recent ssh connection attempts (it checks the file every 2 sec)

## [warning]
Be careful when running ``` nmap ```  because it interrupt the program due to the difference between the packets size.

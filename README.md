# -surl-
A tool that generates a beep sound and prints out a message when someone visits a url on your website or tries to establish an ssh connection with your server.

For the url requests it works with:
  * GET requests only (for now)
  * an ip manager which blocks connections to every host that tries to flood your webserver [ http flood ]

For ssh it:
  * checks the /var/log/auth.log file to see if there are any recent ssh connection attempts (it checks the file every 2 sec)

## [warning]

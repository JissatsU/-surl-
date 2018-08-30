# - About SURL -
A tool that inspects all incoming packets and filters them by ``` dest port ``` and ``` dest ip ```

## - More Info -
For the url requests it works with:
  * GET requests only (for now)
  * an ip manager which blocks connections to every host that tries to flood your webserver [ http flood ]

For ssh it:
  * checks the /var/log/auth.log file to see if there are any recent ssh connection attempts (it checks the file every 2 sec)

# - Usage -              
```
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  -u URL, --url=URL     Specific url connection monitoring.
  -p PORT, --port=PORT  Specify the port for your webserver.
  --ssh=SSH             SSH connection monitoring. [ Works by checking the
                        /var/log/auth.log file ]
  --ip=IP               This option is used in combo with [ --url ].
                        Specifies your IP.
  -i IFACE, --iface=IFACE
                        Bind your interface
  --urls=URLS           Choose your urls file. This file must contain the urls
                        of your website (one on each line) to be matched in
                        the REQUEST
  -b, --block           This option is used in combo with [ --url ]. Choose
                        whether to block connection to hosts if they try to
                        flood [ http ].
  --log-lines=LOG_LINES
                        Number of lines to wait the log file [ all.dat ] to
                        reach before emptying it.
  -l LINE_NUM, --line-num=LINE_NUM
                        Specify the last line num of [ all.dat ] to continue
                        numbering from there.
  --limit=LIMIT         Number of requests per sec. If any ip exceeds the
                        specified number of requests per sec, gets banned.
```


## [warning]
* Be careful when running ``` nmap ```  because it may interrupt the program due to the difference between the packets size!
* Do not edit the files ``` all.dat ``` and ``` blocked.dat ``` unless you know what you're doing!

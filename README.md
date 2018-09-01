# - About SURL -
A tool that inspects all incoming packets, filters them by ``` dest port ``` and ``` dest ip ``` and extracts the ``` requested url ```, ``` request method ``` and ``` protocol ```.


## - More Info -
### For the url requests it works by:
  * parsing GET requests only (for now)
  
  * if the ``` --block ``` option is set it starts an ip manager as a separate process which reads the ``` all.dat ``` file to extract all the hosts with their time intervals and blocks connections to every host that tries to flood your webserver [ http flood ].
  
  * if you set the ``` --log-lines ``` option it will start another process that truncates the file size of ``` all.dat ``` to 0MB when it reaches the number of lines specified in the option.
  
  * creating a file called ``` inf.dat ``` which is used for logging when someone visits the url you specified in the  ``` --url ``` option.
  
  * creating a file called ``` all.dat ``` which is used for logging when the requested url matches any of the urls in the urls file specified in the ``` --urls ``` option.
  
  * creating a file called ``` blocked.dat ``` which is used for logging the blocked ips and to verify that a specific host is blocked. If you remove a host from that file, another ``` iptables ``` rule will be added with the same host.
  

### For ssh it:
  * checks the /var/log/auth.log file to see if there are any recent ssh connection attempts (it checks the file every 2 sec)


## - [Important] -
* You can use both the ``` --url ``` and ``` --urls ``` commands at the same time, but can't do that with both ``` --url ``` and ``` --ssh ```

* When setting the ``` --log-lines ``` option, dont give it a value less than 150.

* The ``` --ssh ``` option is available but won't happen anything because that part of the script is not done yet.

* You have to create the file with all the urls of your site that you want to monitor and give it as a value to ``` --urls ``` option (ex. ``` --urls=my_urls.dat ```).
You can also store the url in your file as a ``` regex ``` by adding ``` [REGEX] ``` at the end.
```
   /
   /index.php
   /admin-panel
   /user/([0-9]*) [REGEX]
   /forum([\?].*) [REGEX]
```


# - Usage -              
```
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  
  -u URL, --url=URL     Specific url connection monitoring.
  
  -p PORT, --port=PORT  Specify the port for your webserver. For --url it defaults to 80 and ssh to 22.
  
  --ssh=SSH             SSH connection monitoring. [ Works by checking the
                        /var/log/auth.log file ]
                        
  --ip=IP               This option is used in combo with [ --url ].
                        Specifies your IP.
                        
  -i IFACE, --iface=IFACE
                        Bind your interface.
                        
  --urls=URLS           Choose your urls file. This file must contain the urls
                        of your website (one on each line) to be matched in
                        the REQUEST, but surl won't notify you, instead it will just log the info in [ all.dat ] 
                        
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
                        Default value of this option is 5.
```


## [warning]
* Be careful when running ``` nmap ```  while this program is running because it may crash the program due to the difference in the packets size!

* Do not edit the files ``` all.dat ``` and ``` blocked.dat ``` after ``` surl ``` creates them unless you know what you're doing!



# - [Prerequisites] -
* ``` sudo apt install ffmepg ```

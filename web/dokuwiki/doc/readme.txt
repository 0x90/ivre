====== What is it? ======

IVRE (Instrument de veille sur les réseaux extérieurs) or DRUNK (Dynamic Recon of UNKnown networks) is a network recon framework, including two modules for passive recon (one [[http://lcamtuf.coredump.cx/p0f/|p0f]]-based and one [[https://www.bro.org/|Bro]]-based) and one module for active recon (mostly [[http://nmap.org/|Nmap]]-based, with a bit of [[https://zmap.io/|ZMap]]).

The advertising slogans are:

  * (in French): IVRE, il scanne Internet.
  * (in English): Know the networks, get DRUNK!

The names IVRE and DRUNK have been chosen as a tribute to "Le Taullier".

===== Disclaimer =====

IVRE is a **framework**. Meaning it does **not** come with ready-to-run scripts to daemonize actions, etc. You need to do that work yourself, as it strongly depends on what system you use, your environment, and what you want to do.

===== External programs / dependencies =====

IVRE relies on:

  * [[http://www.python.org/|Python]] 2, version 2.6 minimum
    * the [[http://www.pycrypto.org/|Crypto]] module
    * the [[http://api.mongodb.org/python/|pymongo]] module,  version 2.7.2 minimum.
  * [[http://nmap.org/|Nmap]] & [[https://zmap.io/|ZMap]]
  * [[http://www.bro.org/|Bro]] & [[http://lcamtuf.coredump.cx/p0f/|p0f]]
  * [[http://www.mongodb.org/|MongoDB]], version 2.6 minimum
  * a web server (successfully tested with [[https://httpd.apache.org/|Apache]] and [[http://nginx.org/|Nginx]], should work with anything capable of serving static files and run a Python-based CGI), although a test web server is now distributed with IVRE (''%%httpd-ivre%%'')
  * a web browser (successfully tested with recent versions of [[https://www.mozilla.org/firefox/|Firefox]] and [[http://www.chromium.org/|Chromium]])
  * Maxmind [[https://www.maxmind.com/en/geolocation_landing|GeoIP]] free databases
  * optionally [[https://code.google.com/p/tesseract-ocr/|Tesseract]], if you plan to add screenshots to your Nmap scan results
  * optionally [[http://www.docker.com/|Docker]] & [[https://www.vagrantup.com/|Vagrant]] (version 1.6 minimum)

IVRE comes with (refer to the [[doc:LICENSE-EXTERNAL|LICENSE-EXTERNAL]] file for the licenses):

  * [[https://angularjs.org/|AngularJS]]
  * [[http://getbootstrap.com/|Twitter Bootstrap]]
  * [[https://jquery.com/|jQuery]]
  * [[http://d3js.org/|D3.js]]
  * [[https://lipis.github.io/flag-icon-css/|flag-icon-css]]

====== Installation ======

See the [[doc:INSTALL|INSTALL]] file. You can also try to use [[doc:DOCKER|Docker]] to easily setup and run an IVRE architecture.

====== Passive recon ======

The following steps will show some examples of **passive** network recon with IVRE. If you only want **active** (for example, Nmap-based) recon, you can skip this part.

===== Using Bro =====

You need to run bro (2.3 minimum) with the option ''%%-b%%'' and the location of the ''%%passiverecon.bro%%'' file. If you want to run it on the ''%%eth0%%'' interface, for example, run:

<code># mkdir logs
# bro -b /usr/local/share/ivre/passiverecon/passiverecon.bro -i eth0</code>
If you want to run it on the ''%%capture%%'' file (''%%capture%%'' needs to a PCAP file), run:

<code>$ mkdir logs
$ bro -b /usr/local/share/ivre/passiverecon/passiverecon.bro -r capture</code>
This will produce log files in the ''%%logs%%'' directory. You need to run a ''%%passivereconworker%%'' to process these files. You can try:

<code>$ passivereconworker --directory=logs</code>
This program will not stop by itself. You can (''%%p%%'')''%%kill%%'' it, it will stop gently (as soon as it has finished to process the current file).

===== Using p0f =====

To start filling your database with information from the ''%%eth0%%'' interface, you just need to run (''%%passiverecon%%'' is just a sensor name here):

<code># p0f2db -s passiverecon iface:eth0</code>
And from the same ''%%capture%%'' file:

<code>$ p0f2db -s passiverecon capture</code>
===== Using the results =====

You have two options for now:

  * the ''%%ipinfo%%'' command line tool
  * the ''%%db.passive%%'' object of the ''%%ivre.db%%'' Python module

For example, to show everything stored about an IP address or a network:

<code>$ ipinfo 1.2.3.4
$ ipinfo 1.2.3.0/24</code>
See the output of ''%%ipinfo --help%%''.

To use the Python module, run for example:

<code>$ python
>>> from ivre.db import db
>>> db.passive.get(db.passive.flt_empty)[0]</code>
For more, run ''%%help(db.passive)%%'' from the Python shell.

====== Active recon ======

===== Scanning =====

The easiest way is to install IVRE on the "scanning" machine and run:

<code># runscans --routable --limit 1000 --output=XMLFork</code>
This will run a standard scan against 1000 random hosts on the Internet by running 30 nmap processes in parallel. See the output of ''%%runscans --help%%'' if you want to do something else.

When it's over, to import the results in the database, run:

<code>$ nmap2db -c ROUTABLE-CAMPAIGN-001 -s MySource -r scans/ROUTABLE/up</code>
Here, ''%%ROUTABLE-CAMPAIGN-001%%'' is a category (just an arbitrary name that you will use later to filter scan results) and ''%%MySource%%'' is a friendly name for your scanning machine (same here, an arbitrary name usable to filter scan results; by default, when you insert a scan result, if you already have a scan result for the same host address with the same source, the previous result is moved to an "archive" collection (fewer indexes) and the new result is inserted in the database).

There is an alternative to installing IVRE on the scanning machine that allows to use several agents from one master. See the [[doc:AGENT|AGENT]] file, the program ''%%runscans-agent%%'' for the master and the ''%%agent/%%'' directory in the source tree.

===== Using the results =====

You have three options:

  * the ''%%scancli%%'' command line tool
  * the ''%%db.nmap%%'' object of the ''%%ivre.db%%'' Python module
  * the web interface

==== CLI: scancli ====

To get all the hosts with the port 22 open:

<code>$ scancli --port 22</code>
See the output of ''%%scancli --help%%''.

==== Python module ====

To use the Python module, run for example:

<code>$ python
>>> from ivre.db import db
>>> db.nmap.get(db.nmap.flt_empty)[0]</code>
For more, run ''%%help(db.nmap)%%'' from the Python shell.

==== Web interface ====

The interface is meant to be easy to use, it has its own [[doc:WEBUI|documentation]].

====== License ======

IVRE is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

IVRE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License [[doc:LICENSE|along with IVRE]]. If not, see [[http://www.gnu.org/licenses/|the gnu.org web site]].

====== Support ======

Try ''%%--help%%'' for the CLI tools, ''%%help()%%'' under Python and the "HELP" button in the web interface.

Feel free to contact the author and offer him a beer if you need help!

If you don't like beer, a good scotch or any other good alcoholic beverage will do (it is the author's unalienable right to decide whether a beverage is good or not).

====== Contributing ======

Code contributions (pull-requests) are of course welcome!

The project needs scan results and capture files that can be provided as examples. If you can contribute some samples, or if you want to contribute some samples and would need some help to do so, or if you can provide a server to run scans, please contact the author.

====== Contact ======

For both support and contribution, the [[https://github.com/cea-sec/ivre|repository]] on Github should be used: feel free to create a new issue or a pull request!

You can also try to use the e-mail ''%%ivre%%'' on the domain ''%%droids-corp.org%%'', or to join the IRC chan [[irc://irc.freenode.net/%23ivre|#ivre]] on [[https://freenode.net/|Freenode]].


----

This file is part of IVRE. Copyright 2011 - 2015 [[mailto:pierre.lalet@cea.fr|Pierre LALET]]


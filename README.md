1.keylogger

Keyloggers are programs that capture your key strokes. They can be used to keep logs of everything you press on the keyboard but on the flip side it can be used for malicious purposes as well.

The keylogger that I've made is a basic keylogger with not much functionality as the ones available in market today. It captures your keystrokes and saves them in a file "keylogger.txt".

It then sends the contents of the file(i.e. the keystrokes) to your email id.

With some extra lines of code, it can also send the keystrokes at regular intervals. But that is a project for another time.

I have not made it executable so one has to explicitely call it.

SYNTAX : python keylogger.py

[NOTE: You need to press esc key to exit out the keylogger.]

You need to have pynput , smtplib and ssl installed.

While python comes with the library smtplib and ssl preinstalled. You can install pynput with : pip install pynput



2.Scanner


These are basic scanners.

They can check the number of devices connected to your network and print their local IP addresses along with their MAC addresses.

Sniff_Tool.py
I have used argparse and scapy to make this basic network scanner.

[Syntax : python <file_name> -ip <ip_address>/<subnet>]

[NOTE : Use it with root/administrative priviledges]

One needs to have argparse and scapy installed.

They can be installed with :

pip install argparse

pip install scapy

OUTPUT :

{'ip': '192.168.1.1', ' mac': '7c:a9:6b:07:6e:14'}

{'ip': '192.168.1.3', ' mac': '88:11:96:ff:79:a0'}

{'ip': '192.168.1.10', ' mac': '68:db:f5:84:80:7f'}

{'ip': '192.168.1.4', ' mac': 'd4:f5:47:17:b0:a6'}

{'ip': '192.168.1.14', ' mac': 'a4:c3:f0:4f:a5:06'}

{'ip': '192.168.1.2', ' mac': '6c:56:97:b0:fe:b3'}

{'ip': '192.168.1.26', ' mac': '28:6c:07:8c:96:f5'}

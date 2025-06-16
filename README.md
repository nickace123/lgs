A GUN/MOUSE Driven Menu for Retropie using existing gamelist.xml

a tkinter/python app to run on linux (in a xorg/x shell)

There is a settings.xml with a selected theme in the root folder and the themes are in the themes folder, ai made one for me the defualt theme.

There is an inscoperoms.xml (which contains all known lightgun rom names.. so it will filter out anything not lightgun related in your gamelist.xml.  
You may not agree with my list and wish to add things.. please go for it.
    
  
  INSTALLATION - On Existing Retropie set up
------------------------------------------------------

1.  Assuming you have all your roms and scrape data in place (gamelist.xml) files in all the rom locations...
2.  Download & Copy the LGS files to a new folder ~/RetroPie/LightGunSystem

4.  You need Python Libraries that are not there by default ... Run the following commands
5.     sudo apt update
6.     sudo apt install python3-tk python3-pygame python3-pip python3-pil.imagetk -y
7.     pip3 install pillow
8.  You need a desktop environment, you can use Pixil, or if you want to keep your retropie system lean and not use a full GUI we will wrap the app in a simple xorg-x
9.   to install xorg...
10.       Run this...  sudo apt install --no-install-recommends xserver-xorg xinit openbox x11-xserver-utils -y
11.       now create this file using NANO, command: nano ~/.xinitrc
12.       contents...
13.   	      #!/bin/bash
	            openbox &
              cd /home/pi/RetroPie/LightGunSystem
	            python3 ./lgs.py
14.       make it executable with command: chmod +x ~/.xinitrc
15.       now typing "startx" from the console will run it.
16.       Would you like to make it run on startup?   There is many ways to do this... my way below
17.           Disable Emulation Station from Running on startup - in retropie_setup select boot to command line (auto logon as user pi only)
18.           Edit existing file with NANO: nano ~/.bashrc
19.          (AT THE BOTTOM)
20.          	if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
          	    startx
	             fi
21.       This will run the command startx for you when you get a command line (that is not SSH)
22.   RECOMMENDED...
23.     Disable Runcommand delays and start images... i have not found a way yet to display them. Do this via retropie_setup / runcommand

I am just a guy who when building a dedicated gun cabinet for myself, was amazed there was nothing like this in existance already. So I made my own gun driven menu and integrated it with Retropie.
I am not a Python Dev, i basically used AI to generate bits and pieces which i spliced together.
This is v1. very out-of-the-box atm...
No License of course. Please use, distribute to your hearts content. develop themes, and If you can improve, mod, enhance, you are more than welcome. please share etc.

Happy Gaming.

#!/bin/bash

# ASCII escape characters
ascii_red=31
ascii_green=32
ascii_yellow=33
ascii_esc="\u1B["

# Colourful logging
function print(){
	if [[ $1 == "Error: "* ]]; then
		color=$ascii_red
	elif [[ $1 == "Warning: "* ]]; then
		color=$ascii_yellow
	else
		color=$ascii_green
	fi
	printf "${ascii_esc}${color}m${1}${ascii_esc}0m\r\n"
}

# Set script's variables
src=$PWD
dir=$(basename $src)
dest=/var/www/html
cwd=$dest/$dir
if [ -z "$SUDO_USER" ]; then
	user=$USER
else
	user=$SUDO_USER
fi

# Check if already installed
if [ -d "$cwd" ]; then
	print "Warning: Folder $cwd exists, seems it is already installed."
	printf "Would you like to remove that directory and reinstall it? (y/n) : "
	read -n 1 -t 10 choice || choice=n
	echo
	if [[ $choice =~ ^(y|Y)$ ]]; then
		sudo rm -r "$cwd"
	else
		print "Installation process finished without changes."
		exit 1
	fi
fi

print "Start dependency fetching of captcha generation ..."
sudo apt install php-gd php -y

print "Start installation configuration ..."
service apache2 restart
sudo adduser www-data $user 1>/dev/null

sudo rsync -r --chmod=640 $src/$dir $dest
sudo chown -R $user:$user $cwd
sudo chmod 770 $cwd
chmod ug+x $cwd/*/
pushd $cwd/solver
chmod u+x *.sh
print "Sources copied into folder ${dest}."

print "Start dependency fetching of captcha processing ..."
sudo apt install python3-pip -y
sudo -H pip3 install launchpadlib six
pip3 install -r requirements.txt

print "Installation process finished successfully."
echo "You can start simulation with next commands:"
echo "pushd $PWD"
echo "./run.sh"

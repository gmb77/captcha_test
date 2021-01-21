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

# Check if already installed
if [ -d "$cwd" ]; then
	printf "Would you like to remove folder $cwd? (y/n) : "
	read -n 1 -t 10 choice || choice=n
	echo
	if [[ $choice =~ ^(y|Y)$ ]]; then
		sudo rm -r "$cwd"
		print "Uninstallation process finished successfully."
	else
		print "Uninstallation process finished without changes."
		exit 1
	fi
fi
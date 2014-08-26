#!/bin/bash

read -p "$1? " filepath
if [[ $filepath == "" ]]
then
	printf "passing \n"
else
	ln -s "$filepath" ../anjuna_symlinks/$1
fi

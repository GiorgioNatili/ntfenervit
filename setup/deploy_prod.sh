#!/bin/bash

echo "## THIS IS PRODUCTION TURNOVER SCRIPT ###"

if [ "$1" != "-w" ]; then
    echo " * ERROR: must pass -w args to run this script"
    exit 1
fi


dest_dir="/var/www/yellowpage"
conf_dir="conf/$dest_dir"

# Create dest directory
if [ ! -d "$dest_dir" ]; then
	echo " * ERROR: $dest_dir does not exists"
	exit 1
fi

# Copy from src to dest_dir
for file in django.wsgi manage.py province.json templatebase.html
do
	echo "### Copying $file"
	cp "./src/$file" "$dest_dir"
done

for dir in backend cabinet campaigns contacts coupon frontend staticfiles survey templates yellowPage
do
	echo "### Copying $dir"
	if [ ! -d "$dest_dir/$dir/" ]; then
		mkdir "$dest_dir/$dir/"
	fi
	rsync -av --delete "./src/$dir/" "$dest_dir/$dir/"
done


if [ ! -d "$dest_dir/media" ]; then
	echo "### Creating $dest_dir/media directory"
	mkdir "$dest_dir/media"
	sudo chown www-data:www-data "$dest_dir/media"
fi

# Done
echo "### COMPLETED"

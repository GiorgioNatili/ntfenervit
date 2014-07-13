#!/bin/bash

dest_dir="dist_test"
conf_dir="conf/$dest_dir"

# Create dest directory
if [ ! -d "$dest_dir" ]; then
	mkdir $dest_dir
fi

# Copy from src to dest_dir
for file in manage.py province.json templatebase.html
do
	echo "### Copying $file"
	cp "./src/$file" "./$dest_dir/"
done

for dir in backend cabinet campaigns contacts frontend staticfiles survey templates yellowPage
do
	echo "### Copying $dir"
	if [ ! -d "./$dest_dir/$dir/" ]; then
		mkdir "./$dest_dir/$dir/"
	fi
	rsync -av --delete "./src/$dir/" "./$dest_dir/$dir/"
done

# Remove the file not used
rm "$dest_dir/yellowPage/settings.py"

# Copy the conf files
cp "$conf_dir/django.wsgi" "$dest_dir/"
cp "$conf_dir/settings_test.py" "$dest_dir/yellowPage/settings_test.py"

# Create and set directory for files
if [ ! -d "$dest_dir/yellowPage/whoosh_index" ]; then
	mkdir "$dest_dir/yellowPage/whoosh_index"
fi

if [ ! -d "$dest_dir/media" ]; then
	echo "### Creating $dest_dir/media directory"
	mkdir "$dest_dir/media"
	sudo chown www-data:www-data "$dest_dir/media"
fi

# Done
echo "### COMPLETED"


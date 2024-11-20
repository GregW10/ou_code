#!/bin/bash

echo "Downloading stuff..."

if ! curl -O -L 'https://veggiebucket.ams3.digitaloceanspaces.com/treewatch_data.tar.gz.enc.sha512'; then
	echo "Download failed of SHA-512 checksum of encrypted file failed.."
fi

if ! curl -O -L 'http://veggiebucket.ams3.digitaloceanspaces.com/treewatch_data.tar.gz.sha512.enc'; then
	echo "Download failed of encrypted SHA-512 checksum of original file."
	exit 1
fi

if ! curl -O -L 'http://veggiebucket.ams3.digitaloceanspaces.com/treewatch_data.tar.gz.enc'; then
	echo "Download of encrypted data failed."
	exit 1
fi

if ! shasum -a 512 -b treewatch_data.tar.gz.enc | diff -q - treewatch_data.tar.gz.enc.sha512; then
	echo "Downloaded file is corrupted."
	exit 1
fi

echo "Attempting to decrypt original file checksum. You will be prompted for the decryption password..."

if ! openssl enc -d -aes-256-cbc -salt -iter 16777216 -in treewatch_data.tar.gz.sha512.enc -out treewatch_data.tar.gz.sha512; then
	echo "Decryption of SHA-512 checksum of original file failed."
	exit 1
fi

if ! shasum -a 512 -b treewatch_data.tar.gz.enc | diff -q - treewatch_data.tar.gz.enc.sha512; then
	echo "Downloaded file is corrupted."
	exit 1
fi

echo "Attempting to decrypt original data file. You will be prompted for the decryption password..."

if ! openssl enc -d -aes-256-cbc -salt -iter 16777216 -in treewatch_data.tar.gz.enc -out treewatch_data.tar.gz; then
	echo "Decryption of data file failed."
	exit 1
fi

if ! shasum -a 512 -b treewatch_data.tar.gz | diff -q - treewatch_data.tar.gz.sha512; then
	echo "Original data file is somehow corrupted."
	exit 1
fi

echo "Files decrypted!"

if [ -e "data" ]; then
	if [ -d "data" ]; then
		dir="$(pwd)/data"
	else
		dir="$(pwd)"
	fi
else
	mkdir data
	dir="$(pwd)/data"
fi

echo "Extracting archive into $dir..."

tar -xvzf treewatch_data.tar.gz -C "$dir/"

exit $?

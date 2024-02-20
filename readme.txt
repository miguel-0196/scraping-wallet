Usage:
--input wallet_list.txt // get wallet info from a given wallet address list file.
--input wallet_files_dir // get wallet info from filenames of wallet files in a given dir.
--loop // keep iterating, don't stop.
--help // usage

If you want to input a lot of wallet list files, you can use following command to merge to one file.
grep -h "[0-9a-fA-F]\{40\}" $(find -name input.txt) > input.txt
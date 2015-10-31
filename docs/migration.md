# Migrating data from Biostar 2 to Biostar 4

There is a migration script in the Biostar 4 source directory
that will migrate all data across the software versions. 
The data are migrated into text files and loaded up 
in the other system.

The paths to directory names
will need to be changed to match your installation.
We label them as `biostar2-central` and `biostar4-central`

For the migration to work your system needs to be
able to run different python environments. At the
very least you need to have be able to run `python 2.7` for the
Biostar 2 and `python 3.4` to run Biostar 4. 

To avoid confusion we will explicitly label the python 
versions as `python2`, `pip2` and `python3` and `pip3`.

1. Enable the environment that Biostar 2 runs in. 
	
		# Switch to the biostar 2 repository.
		cd ~/app/biostar2-central
		
		# Set up the migration specific dependencies.
		pip2 install markdown2 html2text
		
		# Load the environment.
		source conf/defaults.env 
		
		# Print the current environment.
		./biostar.sh env
		
		# Add the biostar 2 source directory to the python path
		export PYTHONPATH=.:$PYTHONPATH
		
2. Export the data into flat files:

		# Run the migrate script in the biostar 2 source directory:
		
		# It will show the settings will be used for migrating the data.
		python2 ~/app/biostar4-central/bin/export_b2.py
		
		# Export the data into files.
		mkdir ~/tmp/data
		python2 ~/app/biostar4-central/bin/export_b2.py --dest ~/tmp/data
		
2. Import the data from the flatfiles

		cd ~/app/biostar4-central

		# Perform the migration.
		python3 -m biostar4.manage import_biostar2 



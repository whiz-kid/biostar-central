# Migrating data from Biostar 2 to Biostar 4

There is a migration script in the Biostar 4 source directory
that will migrate all data across the software versions. 

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
		pip2 install mongoengine html2text click markdown2
		
		# Load the environment.
		source conf/defaults.env 
		
		# Print the current environment.
		./biostar.sh env
	
2. Add `mongodb` specific settings to the biostar 2 settings file.

		SETTINGS=~/app/biostar2-central/biostar/settings/base.py
		echo 'MONGODB_NAME = os.getenv("MONGODB_NAME", "test")' >> $SETTINGS
		echo 'MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/test")' >> $SETTINGS
		
3. Add both the biostar 2 and biostar 4 source directories to the python import path:

		export PYTHONPATH=~/app/biostar2-central:~/app/biostar4-central/
		
4. Run the migrate script from the biostar 2 source directory:

		# Change to the biostar 2 repository
		cd ~/app/biostar2-central
		
		# Run the migration script from the biostar 4 directory.
		# It will show the settings will be used for migrating the data.
		python2 ~/app/biostar4-central/biostar4/run/migrate.py 
		
		# See help for migration parameters:
		python2 ~/app/biostar4-central/biostar4/run/migrate.py --help
		
		# Perform the migration.
		python2 ~/app/biostar4-central/biostar4/run/migrate.py --drop --migrate



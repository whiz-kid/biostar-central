# Biostar 4

## Biostar: Software for Building Scientific Communities

Branch 4.0 rewrite. Under heavy development. See:
https://github.com/ialbert/biostar-central/issues/291

Features may not always work. Docs may be out of sync.
We'll clean it up by the first release.

Python 3, Django and [MongoDB][mongodb] based Q&A site.

Test site (may be on or off): http://test.biostars.org

[mongodb]: https://www.mongodb.org/

## Install

1. Get `mongodb` working on a computer.  

2. Install the requirements:
	
		pip3 install -r requirements.txt
 	
3. Run the server

		# To check your settings use:
		python3 -m biostar4.manage verify
	
		# Run the development server on port 8080.
		python3 -m biostar4.manage runserver 8080
	 
4. Most settings values will pulled from the environment if available: `MONGODB_NAME`, `MONGODB_URL` etc.
   For details see:

		more biostar4/settings.py

# Documentation

* [Migrating from Biostar 2](docs/migration.md)
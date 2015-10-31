## Biostar: Software for Building Scientific Communities

[![Build Status][build-image]][build-url] 
[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)

[build-image]: https://travis-ci.org/ialbert/biostar-central.svg?branch=4.0
[build-url]: https://travis-ci.org/ialbert/biostar-central/builds

Branch 4.0 rewrite. Under heavy development. See:
https://github.com/ialbert/biostar-central/issues/291

Features may not always work. Docs may be out of sync.
We'll clean it up by the first release.

Python 3, Django based Q&A site.

Test site (may be on or off): http://test.biostars.org


## Install

2. Install the requirements:
	
        pip3 install -r conf/requirements.txt
 	
3. Run the server

		# Show your current environment:
		python3 -m biostar4.manage env

		# To initialize the database:
		python3 -m biostar4.manage init
	 
		# Run the development server on port 8080.
		python3 -m biostar4.manage runserver 8080
	 
4. Most settings values will pulled from the environment if available.
   For details see:

		more biostar4/settings/base.py

## Documentation

* [Migrating from Biostar 2](docs/migration.md)
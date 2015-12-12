all: run

SRC=biostar4
PYZ=biostar4.pyz

run: pack
	python ${PYZ} runserver 8080

pack:
	python -m zipapp ${SRC} 

clean:
	rm -f ${PYZ}

list:
	unzip -l ${PYZ}

wheels:
	#mkdir -p conf/wheel
	#pip wheel -r conf/requirements.txt --wheel-dir conf/wheel
	find conf/wheel -name '*.whl' -exec unzip -o {} -d conf/wheel \;


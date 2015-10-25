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


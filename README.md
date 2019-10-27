# Unicat

This repository includes...

* Unicat Interpreter
* Unicat Compiler 
* Unicat Decompiler


Original unicat from [here](https://github.com/gemdude46/unicat)

## Catpiler

This is a simple Unicat compiler. You can generate Unicat code from assembly-like language.

## Usage
#### compile
```
$ python3 catpiler.py ../examples/star.cata -o ../examples/star.cat
```

#### run
```
$ python3 unicat.py ../examples/star.cat
5
*
**
***
****
*****
```

#### decompile
```
$ python decatpiler.py ../examples/star.cat
```
SHELL := /bin/bash

submodule_obj := ./aggregables/sequences/suffix_trees/suffix_trees/STree.py

all: $(submodule_obj)

submodule_init:
	git submodule add https://github.com/nevesnunes/suffix-trees.git ./aggregables/sequences/suffix_trees
	cd ./aggregables/sequences/suffix_trees
	git checkout lrs
	cd ../..
	git add ./aggregables/sequences/suffix_trees

$(submodule_obj):
	git submodule update --init --recursive

.DEFAULT_GOAL := all
.PHONY: all submodule_init

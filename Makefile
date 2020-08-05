SHELL := /bin/bash

submodule_suffix_tree := ./sequences/suffix_trees

all: $(submodule_suffix_tree)

submodule_init:

$(submodule_suffix_tree):
	git submodule add https://github.com/nevesnunes/suffix-trees.git ./sequences/suffix_trees
	cd ./sequences/suffix_trees
	git checkout lrs
	cd ../..
	git add ./sequences/suffix_trees

.DEFAULT_GOAL := all
.PHONY: all submodule_init

#/***************************************************************************
# StreamFeatureExtractor
#
# A tool to extract features from a stream network.
#							 -------------------
#		begin				: 2014-05-07
#		copyright			: (C) 2014 by Linfiniti Consulting CC.
#		email				: tim@linfiniti.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


#Add iso code for any locales you want to support here (space separated)
LOCALES = en af de id

PLUGINNAME = StreamFeatureExtractor

PY_FILES = \
	__init__.py \
	stream_feature_extractor.py\
	stream_options_dialog.py \
	stream_help_dialog.py\
	stream_utilities.py\
	custom_logging.py

EXTRAS = icon.png metadata.txt LICENSE README.md

STYLES = styles

UI_FILES = \
	stream_options_dialog_base.ui\
	stream_help_dialog_base.ui

COMPILED_RESOURCE_FILES = resources_rc.py

# For debug deploys
PYDEV = pydev

#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/build/html

THIRD_PARTY = third_party

PLUGIN_UPLOAD = $(c)/plugin_upload.py

QGISDIR=.qgis2

default: compile

compile: $(COMPILED_RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

test: test_code pep8 pylint

test_code: compile transcompile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:`pwd`/third_party:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		nosetests -v --exclude pydev --with-id --with-coverage \
		--cover-package= . \
		3>&1 1>&2 2>&3 3>&- || true

deploy: compile doc transcompile compile_qml_styles
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis2 directory."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/i18n
	cp -vfr i18n/*.qm $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/i18n/
	cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help
	cp -vfr $(STYLES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/styles
	cp -vfr $(THIRD_PARTY) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/

debugdeploy: deploy
	@echo
	@echo "------------------------------------------"
	@echo "Deploying pydev debug libs."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -rvf $(PYDEV) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr $(THIRD_PARTY) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/third_party

# The dclean target removes compiled python files from plugin directory
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete

derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@scripts/update-strings.sh $(LOCALES)

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@scripts/compile-strings.sh $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_RESOURCE_FILES)

doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd help; make clean; make html

# Note that make runs commands in a subshell so 
# variable context is lost from one line to the next
# So we need to do everything as a single line command 
tag:
	@echo
	@echo "------------------------------------"
	@echo "Tagging the release."
	@echo "------------------------------------"
	@read -p "Version e.g. 1_0_0: " VERSION; \
	git tag -s version-$$VERSION -m "Version $$VERSION" && \
	git push --tags origin version-$$VERSION
	
pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . | \
		grep -v locally-disabled || true


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude conf.py,pydev,resources_rc.py,third_party . || true

compile_qml_styles:
	@echo
	@echo "-----------------------------------------"
	@echo "Compile qml styles for supported locales."
	@echo "-----------------------------------------"
	@PYTHONPATH=. python scripts/translate_style.py $(LOCALES)

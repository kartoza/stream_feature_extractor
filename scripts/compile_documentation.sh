#!/bin/bash
# Next line is a trick to get absolute path from relative path
# http://stackoverflow.com/questions/4045253/converting-relative-path-into-absolute-path
export QGIS_PREFIX_PATH=/usr/local/qgis-2.0

export LD_LIBRARY_PATH=$QGIS_PREFIX_PATH/lib
export PYTHONPATH=$QGIS_PREFIX_PATH/share/qgis/python:$INASAFE_DEV_PATH:$QGIS_PREFIX_PATH/share/qgis/python/plugins:$PYTHONPATH
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/dev/null
export QGIS_DEBUG_FILE=/dev/null

echo "LIBRARY_PATH="$LD_LIBRARY_PATH
echo "PYTHONPATH="$PYTHONPATH

# Based off the script from QGIS by Tim Sutton and Richard Duivenvoorde

# Name of the dir containing static files
STATIC=_static
# Path to the documentation root relative to script execution dir
DOCROOT=help
# Path from execution dir of this script to docs sources (could be just
# '' depending on how your sphinx project is set up).
SOURCE=source
# Current dir - pdf will be copied to here
CURRENT_DIR=`pwd`

pushd .
cd $DOCROOT

SPHINXBUILD=`which sphinx-build`
TEXI2PDF=`which texi2pdf`

# GENERATE PDF AND HTML FOR FOLLOWING LOCALES (EN IS ALWAYS GENERATED)
LOCALES='de id'

if [ $1 ]; then
  LOCALES=$1
fi

BUILDDIR=build
# be sure to remove an old build dir
rm -rf ${BUILDDIR}
mkdir -p ${BUILDDIR}

# output dirs
PDFDIR=`pwd`/output/pdf
HTMLDIR=`pwd`/output/html
mkdir -p ${PDFDIR}
mkdir -p ${HTMLDIR}

VERSION=`cat source/conf.py | grep "version = '.*'" | grep -o "[0-9]\.[0-9]"`

if [[ $1 = "en" ]]; then
  echo "Not running localization for English."
else
  for LOCALE in ${LOCALES}
  do
    for POFILE in `find i18n/${LOCALE}/LC_MESSAGES/ -type f -name '*.po'`
    do
      MOFILE=`echo ${POFILE} | sed -e 's,\.po,\.mo,'`
      # Compile the translated strings
      echo "Compiling messages to ${MOFILE}"
      msgfmt --statistics -o ${MOFILE} ${POFILE}
    done
  done
fi

# We need to flush the build dir or the translations don't come through
rm -rf ${BUILDDIR}
mkdir ${BUILDDIR}
#Add english to the list and generated docs
LOCALES+=' en'

if [ $1 ]; then
  LOCALES=$1
fi

for LOCALE in ${LOCALES}
# Compile the html docs for this locale
do
  echo "Building docs for locale: $LOCALE"
  # cleanup all images for the other locale
  rm -rf source/static
  mkdir -p source/static
  # copy english (base) resources to the static dir
  cp -r resources/en/* source/static
  # now overwrite possible available (localised) resources over the english ones
  cp -r resources/${LOCALE}/* source/static


  #################################
  #
  #        HTML Generation
  #
  #################################

  echo "Building HTML for locale '${LOCALE}'..."
  LOG=/tmp/sphinx$$.log
  ${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b html source ${HTMLDIR}/${LOCALE} > $LOG
  WARNINGS=`cat $LOG | grep warning`
  ERRORS=`cat $LOG | grep ERROR`
  if [[  $WARNINGS ]]
  then
    echo "***********************************************"
    echo "* Sphinx build produces warnings - Please fix *"
    echo $WARNINGS
    echo "***********************************************"
    exit 1
  fi
  if [[  $ERRORS ]]
  then
    echo "*********************************************"
    echo "* Sphinx build produces errors - Please fix *"
    echo $ERRORS
    echo "*********************************************"
    exit 1
  fi

  #################################
  #
  #         PDF Generation
  #
  #################################
  # experimental sphinxbuild using rst2pdf...
  #${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b pdf source ${BUILDDIR}/latex/${LOCALE}

  # Traditional using texi2pdf....
  # Compile the latex docs for that locale
  ${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b latex source ${BUILDDIR}/latex/${LOCALE}  > /dev/null 2>&1
  # Compile the pdf docs for that locale
  # we use texi2pdf since latexpdf target is not available via
  # sphinx-build which we need to use since we need to pass language flag
  pushd .
  #cp resources/InaSAFE_footer.png ${BUILDDIR}/latex/${LOCALE}/
  #cd ${BUILDDIR}/latex/${LOCALE}/
  # Manipulate our latex a little - first add a standard footer

  #FOOTER1="\usepackage{wallpaper}"
  #FOOTER2="\LRCornerWallPaper{1}{InaSAFE_footer.png}"

  # need to build 3x to have proper toc and index
  if [ -z $TEXI2PDF ]
    then
      echo You do not have texinfo package installed. Please install!
      exit 1
  fi

  echo "Building PDF's in " `pwd`
  texi2pdf --quiet StreamFeatureExtractor.tex > /dev/null 2>&1
  texi2pdf --quiet StreamFeatureExtractor.tex > /dev/null 2>&1
  texi2pdf --quiet StreamFeatureExtractor.tex > /dev/null 2>&1
  cp StreamFeatureExtractor.pdf $CURRENT_DIR
  popd
done

rm -rf source/static
#rm -rf ${BUILDDIR}

popd

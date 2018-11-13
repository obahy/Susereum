#!/bin/sh

cd log4cplus-1.1.0

make distclean

export SM_DISABLE_ANALYSIS=true
./configure
unset SM_DISABLE_ANALYSIS

make

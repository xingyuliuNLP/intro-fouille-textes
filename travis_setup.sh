#!/bin/bash

 # setup script to install texlive and add to path
 texlive_year="2018"

 export PATH=/tmp/texlive/bin/x86_64-linux:$PATH

 if ! command -v pdflatex > /dev/null; then
     echo "Texlive not installed"
     echo "Downloading texlive and installing"
     wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
     tar -xzf install-tl-unx.tar.gz
     ./install-tl-*/install-tl --profile=./texlive.profile

     echo "Finished install TexLive"
 fi

 echo "Now updating TexLive"
 # update texlive
 tlmgr option -- autobackup 0
 tlmgr update --self --all --no-auto-install

 echo "Finished updating TexLive"

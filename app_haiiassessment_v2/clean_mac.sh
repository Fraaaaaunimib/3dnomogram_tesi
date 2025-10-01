#!/bin/bash

FOLDER_PATH1=./static/output1
FOLDER_PATH2=./static/output2
FOLDER_PATH3=./static/output3
FOLDER_PATH4=./templates/user-generated
FOLDER_PATH5=./uploads
FOLDER_PATH6=./static/output4

MAX_SIZE=16500000 # 16,5MB
SLEEP_TIME=3600 # 1 ora in secondi


folder_size1=$(du -m $FOLDER_PATH1 2>/dev/null | awk '{print $1}')
folder_size2=$(du -m $FOLDER_PATH2 2>/dev/null | awk '{print $1}')
folder_size3=$(du -m $FOLDER_PATH3 2>/dev/null | awk '{print $1}')
folder_size4=$(du -m $FOLDER_PATH4 2>/dev/null | awk '{print $1}')
folder_size5=$(du -m $FOLDER_PATH5 2>/dev/null | awk '{print $1}')
folder_size6=$(du -m $FOLDER_PATH6 2>/dev/null | awk '{print $1}')

find $FOLDER_PATH1 -not -name '.gitkeep' -mmin +119 -delete > /dev/null 2>&1
find $FOLDER_PATH2 -not -name '.gitkeep' -mmin +119 -delete > /dev/null 2>&1
find $FOLDER_PATH3 -not -name '.gitkeep' -mmin +119 -delete > /dev/null 2>&1
find $FOLDER_PATH4 -not -name '.gitkeep' -mmin +119 -delete > /dev/null 2>&1
find $FOLDER_PATH5 -not -name '.gitkeep' -mmin +5  -delete > /dev/null 2>&1
find $FOLDER_PATH6 -not -name '.gitkeep' -mmin +119 -delete > /dev/null 2>&1


folder_size1=${folder_size1:-0}
folder_size2=${folder_size2:-0}
folder_size3=${folder_size3:-0}
folder_size4=${folder_size4:-0}
folder_size5=${folder_size5:-0}
folder_size6=${folder_size6:-0}


if [ $((folder_size1+folder_size2+folder_size3+folder_size4+folder_size5+folder_size6)) -gt $MAX_SIZE ]
then

find $FOLDER_PATH1 -not -name '.gitkeep' -delete > /dev/null 2>&1
find $FOLDER_PATH2 -not -name '.gitkeep' -delete > /dev/null 2>&1
find $FOLDER_PATH3 -not -name '.gitkeep' -delete > /dev/null 2>&1
find $FOLDER_PATH4 -not -name '.gitkeep' -delete > /dev/null 2>&1
find $FOLDER_PATH5 -not -name '.gitkeep' -delete > /dev/null 2>&1
find $FOLDER_PATH6 -not -name '.gitkeep' -delete > /dev/null 2>&1

fi
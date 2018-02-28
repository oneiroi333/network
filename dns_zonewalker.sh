#!/bin/bash

while getopts "t:o:" opt
do
	case $opt in
		t)
			START_DOMAIN=$OPTARG
			;;
		o)
			OUTPUT_FILE=$OPTARG
			;;
		\?)
			echo "Usage: $0 -t <target> [-o <output_file>]"
			exit 1
			;;
	esac
done

if [ -z "$START_DOMAIN" ]
then
	echo "Usage: $0 -t <target> [-o <output_file>]"
	exit 1
fi

NEXT_DOMAIN=$(dig $START_DOMAIN ANY | grep -m 1 NSEC | awk '{print $5}')
if [ -z "$OUTPUT_FILE" ]
then
	echo $NEXT_DOMAIN
else
	echo $NEXT_DOMAIN >> $OUTPUT_FILE
fi
while [ "$NEXT_DOMAIN" != "$START_DOMAIN" ]
do
	NEXT_DOMAIN=$(dig $NEXT_DOMAIN ANY | grep -m 1 NSEC | awk '{print $5}')

	# Valid if the domainname includes the domain
	if [[ "$NEXT_DOMAIN" =~ "$START_DOMAIN" ]]
	then
		if [ -z "$OUTPUT_FILE" ]
		then
			echo $NEXT_DOMAIN
		else
			echo $NEXT_DOMAIN >> $OUTPUT_FILE
		fi
	else
		break
	fi
done

exit 0

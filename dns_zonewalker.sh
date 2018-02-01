#!/bin/bash

# Standard out

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
			echo "Invalid option: -$OPTARG" >&2
			;;
	esac
done

NEXT_DOMAIN=$START_DOMAIN

NEXT_DOMAIN=$(dig $NEXT_DOMAIN ANY | grep -m 1 NSEC | awk '{print $5}')
if [ -z "$OUTPUT_FILE" ]
then
	echo $NEXT_DOMAIN
else
	echo $NEXT_DOMAIN >> $OUTPUT_FILE
fi
while [ "$NEXT_DOMAIN" != "$START" ]
do
	NEXT_DOMAIN=$(dig $NEXT_DOMAIN ANY | grep -m 1 NSEC | awk '{print $5}')

	# Full cycle completed
	if [ "$NEXT_DOMAIN" == "$START_DOMAIN" ]
	then
		break
	fi

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

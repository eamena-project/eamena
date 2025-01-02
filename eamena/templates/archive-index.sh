#!/bin/bash

yestdate=$( date -d "yesterday 13:00 " '+%Y-%m-%d' ) ; indexfile="_index.htm"
index_old=${yestdate}${indexfile}
mv index.htm ./archives/$index_old

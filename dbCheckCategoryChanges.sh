#!/bin/bash

RECIPIENTS=$(echo "$@" | tr ' ' ',')
HOSTNAME=$(hostname -f)
MUTT_SENDER="set from='support@sonassi.com' realname='$HOSTNAME | Sonassi'"

/usr/local/bin/n98-magerun2 --root-dir="/microcloud/domains/corney/domains/corneyandbarrow.com/http" db:query '
Select category_id, product_id from catalog_category_product order by product_id
' > /home/www-data/category_diff_current.txt

diff -u /home/www-data/category_diff_current.txt /home/www-data/category_diff_previous.txt | grep -E "^\-" > /home/www-data/category_diff_report.txt

# Check if file is empty or not
if [[ $(wc -l < /home/www-data/category_diff_report.txt) -ge 20 ]]
then
    # file is not empty, send a mail with the attachment
    cat /home/www-data/category_diff_report.txt | mutt -e "$MUTT_SENDER" -a /home/www-data/category_diff_current.txt -a /home/www-data/category_diff_previous.txt -s "C+B Categories have changed" -- $RECIPIENTS
fi

# clean up everything
rm /home/www-data/category_diff_report.txt /home/www-data/category_diff_previous.txt
mv /home/www-data/category_diff_current.txt /home/www-data/category_diff_previous.txt

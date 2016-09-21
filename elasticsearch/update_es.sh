#!/bin/bash
if [ -L "$0" ]
then
    app_path=$(dirname -- "$(readlink -m -- "$0")")
else
    app_path=$(dirname -- "$0")
fi
cd -P -- "$app_path"
app_path=`pwd -P`

host=10.0.1.12:9200

function create_index()
{
    local day=$1
    curl -XPOST -d @index.js "http://$host/$day" 2>/dev/null
    echo 
    mkdir -p tmp
    #for type in s1 s5 s6 a1 a2 e3 e6 s2 s9 u1
    #原本是设备类型，已经匿名处理
    for type in default
    do
        rm -rf tmp/*
        cp type_class.js tmp/type_instance.js
        sed -i "s/INSTANCE_NAME_BE_REPLACED_HERE/$type/" tmp/type_instance.js
        curl -XPOST -d @tmp/type_instance.js "http://$host/$day/$type/_mapping" 2>/dev/null
    done
    rm -rf tmp
}


function delete_index()
{
    local day=$1
    curl -XDELETE "http://$host/$day"
}

cur_ts=$(date +%s)

cd $app_path

# create for last 30 days, today, and tomorrow
delta=-16
while [ $delta -lt 2 ]
do
    t=$((cur_ts + delta * 86400))
    day=$(date --date @$t +%Y%m%d)
    create_index $day
    echo "index $day created"
    delta=$((delta + 1))
done


# delete
delta=-17
while [ $delta -gt -60 ]
do
    t=$((cur_ts + delta * 86400))
    day=$(date --date @$t +%Y%m%d)
    delete_index $day
    echo "index $day delete"
    delta=$((delta - 1))
done


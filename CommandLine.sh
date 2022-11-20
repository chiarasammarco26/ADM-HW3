#!/bin/bash

countries=("Italy" "Spain" "France" "England" "United States")
for country in "${countries[@]}";
do
    country="${country}"
    echo Country: "${country}"

    echo i. Number of places can be found in "${country}":
    number_places=$(cut -f 3,4,8 place_i.tsv | grep "${country}" | wc -l)
    echo $number_places

    i=0
    for numPeopleVisited in $(cut -f 3,4,8 place_i.tsv | grep "${country}" | cut -f 1); do
    i=$(($i+$numPeopleVisited))
    done
    
    echo ii. Number of people, on average, have visited the places in "${country}":
    i=$(($i / $number_places))
    echo $i

    k=0
    for numPeopleWant in $(cut -f 3,4,8 place_i.tsv | grep "${country}" | cut -f 2); do
    k=$(($k + $numPeopleWant))
    done
    
    echo iii. Number of people in total want to visit the "${country}":
    echo $k
    echo "----------------------------------------------------------------"
done



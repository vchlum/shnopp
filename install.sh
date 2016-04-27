#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

DESTINATIONS=(osmc@osmc-obyvaci-pokoj osmc@osmc-loznice)

for i in ${DESTINATIONS[*]}; do 
    read -r -p "Install shnopp to ${i}? [y/N] " response
    case $response in
    [yY][eE][sS]|[yY]) 
        echo "Kopiruji..."
        ;;
    *)
        echo "Skipping ${i}..."
        continue
        ;;
    esac

    ssh ${i} "rm -r ~/shnopp"
    #ssh ${i} "mkdir -p ~/shnopp"
    
    scp -pr $DIR ${i}:~/
    
    if [[ "$i" == "osmc@osmc-obyvaci-pokoj" ]]; then
        ssh ${i} "rm ~/.kodi/addons/service.shnopp-kodi/config"
        ssh ${i} "rm ~/.kodi/addons/service.shnopp-kodi/misc"
        ssh ${i} "rm ~/.kodi/addons/service.shnopp-kodi"
        ssh ${i} "ln -s ~/shnopp/service.shnopp-kodi/ ~/.kodi/addons/service.shnopp-kodi"
        ssh ${i} "ln -s ~/shnopp/config/ ~/.kodi/addons/service.shnopp-kodi/config"
        ssh ${i} "ln -s ~/shnopp/misc/ ~/.kodi/addons/service.shnopp-kodi/misc"
    fi

    if [[ "$i" == "osmc@osmc-loznice" ]]; then
        ssh ${i} "rm ~/.kodi/addons/service.sc-np10"
        ssh ${i} "ln -s ~/shnopp/service.sc-np10/ ~/.kodi/addons/service.sc-np10"
    fi
done

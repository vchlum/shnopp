#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

DESTINATIONS=(osmc@osmc-obyvaci-pokoj osmc@osmc-loznice)

for i in ${DESTINATIONS[*]}; do 
    read -r -p "Install shnopp to ${i}? [y/N] " response
    case $response in
    [yY][eE][sS]|[yY]) 
        echo "Copying..."
        ;;
    *)
        echo "Skipping ${i}..."
        continue
        ;;
    esac

    ssh ${i} "rm -rf ~/shnopp"
    
    scp -pr $DIR ${i}:~/    
    
    home_dir=$(ssh ${i}  "cd ~/; pwd")
    ssh ${i} "sudo rm -rf /etc/init.d/shnopp"
    ssh ${i} "sudo ln -s ${home_dir}/shnopp/shnoppinit /etc/init.d/shnopp"
    #ssh ${i} "sudo update-rc.d shnopp defaults"
    #ssh ${i} "sudo update-rc.d shnopp enable"
    ssh ${i} "sudo /etc/init.d/shnopp restart"    
    
    if [[ "$i" == "osmc@osmc-obyvaci-pokoj" ]]; then
        ssh ${i} "rm -f ~/.kodi/addons/service.shnopp-kodi/config"
        ssh ${i} "rm -f ~/.kodi/addons/service.shnopp-kodi/misc"
        ssh ${i} "rm -f ~/.kodi/addons/service.shnopp-kodi"
        ssh ${i} "ln -s ~/shnopp/service.shnopp-kodi/ ~/.kodi/addons/service.shnopp-kodi"
        ssh ${i} "ln -s ~/shnopp/config/ ~/.kodi/addons/service.shnopp-kodi/config"
        ssh ${i} "ln -s ~/shnopp/misc/ ~/.kodi/addons/service.shnopp-kodi/misc"

        ssh ${i} "sudo systemctl start mediacenter"
    fi

    if [[ "$i" == "osmc@osmc-loznice" ]]; then
        ssh ${i} "rm -f ~/.kodi/addons/service.sc-np10"
        ssh ${i} "ln -s ~/shnopp/service.sc-np10/ ~/.kodi/addons/service.sc-np10"

        ssh ${i} "sudo systemctl start mediacenter"
    fi
    
done

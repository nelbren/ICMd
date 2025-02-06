#!/bin/bash

# config.bash v1.1 @ 2025-02-05 - nelbren@nelbren.com

myEcho() {
    tag="$1"
    printf "$tag${S}\n"
}

colors_set() {
    S="\e[0m";E="\e[K";n="$S\e[38;5";N="\e[9";e="\e[7";I="$e;49;9"
    A=7m;R=1m;G=2m;Y=3m;nW="$N$A";nR="$N$R";nG="$N$G";nY="$N$Y"
    Iw="$I$A";Ir="$I$R";Ig="$I$G";Iy="$I$Y" 
}

config_install() {
    printf "${nW}config.yml...${S}"
    if [ ! -r config.yml ]; then
        myEcho ${nY}'☐'
        printf "\n${Iw}cp config.yml.example config.yml${S}\n"
        cp config.yml.example config.yml
        if [ ! -r config.yml ]; then
            myEcho ${nR}'×'
            printf "\n${nY}Please manually copy config! ( cp config.yml.example config.yml )${S}\n"
            exit 1
        fi 
    else
        myEcho ${nG}'✓'
        printf "${nW}INSTRUCTURE_URL...${S}"
        if grep -q replace-with-your-INFRASTRUCTURE-URL_and_rename_this_file config.yml; then
            myEcho ${nR}'×'
            printf "\n${nY}Change INSTRUCTURE_URL in config.yml!${S}\n"
            exit 2
        else
            myEcho ${nG}'✓'
        fi
        printf "${nW}API_KEY...........${S}"
        if grep -q replace-with-your-KEY_API_and_rename_this_file config.yml; then
            myEcho ${nR}'×'
            printf "\n${nY}Change API_KEY in config.yml!${S}\n"
            exit 3
        else
            myEcho ${nG}'✓'
        fi
        printf "${nW}COURSE_ID.........${S}"
        if grep -q replace-with-your-COURSE_ID_and_rename_this_file config.yml; then
            myEcho ${nR}'×'
            printf "\n${nY}Change COURSE_ID in config.yml!${S}\n"
            exit 4
        else
            myEcho ${nG}'✓'
        fi
        printf "${nW}ASSIGNMENT_ID....${S}"
        if grep -q replace-with-your-ASSIGNMENT_ID_and_rename_this_file config.yml; then
            myEcho ${nR}'×'
            printf "\n${nY}Change ASSIGNMENT_ID in config.yml!${S}\n"
            exit 4
        else
            myEcho ${nG}'✓'
        fi
    fi
}

colors_set
config_install
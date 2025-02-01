#!/bin/bash

# install.bash v1.5 @ 2024-11-29 - nelbren@nelbren.com

myEcho() {
    tag="$1"
    printf "$tag${S}\n"
}

colors_set() {
    S="\e[0m";E="\e[K";n="$S\e[38;5";N="\e[9";e="\e[7";I="$e;49;9"
    A=7m;R=1m;G=2m;Y=3m;nW="$N$A";nR="$N$R";nG="$N$G";nY="$N$Y"
    Iw="$I$A";Ir="$I$R";Ig="$I$G";Iy="$I$Y" 
}

python_install() {
    printf "${nW}Python Install....${S}"
    if ! python -V 1>/dev/null 2>/dev/null; then
        myEcho ${nR}'×'
        printf "\n${nY}Please manually install Python (>= 3.12)${S}\n"
        exit 1
    else
        myEcho ${nG}'✓'
    fi
}

venv_Scripts_fix() {
    if [ -r .venv/bin/activate ]; then
        if [ ! -d .venv/Scripts ]; then
            mkdir .venv/Scripts
        fi
        ln -s ../bin/activate .venv/Scripts/activate
    fi
}

venv_install() {
    printf "${nW}Python Venv.......${S}"
    if [ ! -r .venv/Scripts/activate ]; then
        venv_Scripts_fix
        if [ ! -r .venv/Scripts/activate ]; then
            myEcho ${nY}'☐'
            printf "\n${Iw}python -m venv .venv${S}\n"
            python -m venv .venv
            printf "${nW}Python Venv.......${S}"
            venv_Scripts_fix
            if [ ! -r .venv/Scripts/activate ]; then
	            myEcho ${nR}'×'
                printf "\n${nY}Please manually make my virtual environment! ( python -m venv .venv )${S}\n"
                exit 2
            else
                myEcho ${nG}'✓'
            fi
        else
            myEcho ${nG}'✓'
        fi
    else
        myEcho ${nG}'✓'
    fi
}

pip_update() {
    source .venv/Scripts/activate
    printf "${nW}Pip Updated.......${S}"
    if pip list --outdated 2>/dev/null | grep pip 1>/dev/null 2>/dev/null; then
        myEcho ${nY}'☐'
        printf "\n${Iw}python -m pip install --upgrade pip${S}\n"
        python -m pip install --upgrade pip
        printf "${nW}Pip Updated.......${S}"
        if pip list --outdated 2>/dev/null | grep pip 1>/dev/null 2>/dev/null; then
            myEcho ${nR}'×'
            printf "\n${nY}Please manually update pip! ( python -m pip install --upgrade pip )${S}\n"
            exit 3
        else
            myEcho ${nG}'✓'
        fi
    else
        myEcho ${nG}'✓'
    fi
}

module_install() {
    module=$1
    # /install.bash: line 49: -1: substring expression < 0
    len=${#module}
    len=$((len - 1))
    #module=${module:0:$len}
    import=$2
    moduleNumber=$3
    if [ "$moduleNumber" == "0" ]; then
        reporte="${reporte}$module..."
    else
        reporte="${reporte}, $module..."
    fi
    if ! python -c "import $import" 1>/dev/null 2>/dev/null; then
        reporte="$reporte ${nY}☐${S}"
        printf "\n${Iw}pip install $module${S}\n"
        pip install $module
        if ! python -c "import $import" 1>/dev/null 2>/dev/null; then
            reporte="${reporte}${nR}×${S} ${nY}( pip install $module )${S}"
            # exit 3
        else
            reporte="$reporte ${nG}✓${S}"
        fi
    else
        reporte="$reporte ${nG}✓${S}"
    fi
}

modules_install() {
    source .venv/Scripts/activate
    reporte="${nW}Python Modules....(${S}"
    error=0
    moduleNumber=0
    while read module comentario import; do
        # echo "MODULE->$module IMPORT->$import MODULENUMBER->$moduleNumber"
        if [ -z "$import" ]; then
           import=$module
        fi
        module_install $module $import $moduleNumber
        moduleNumber=$((moduleNumber + 1))
    done < requirements.txt
    printf "$reporte) "
    if [ "$error" == "0" ]; then
        myEcho ${nG}'✓'
    else
        myEcho ${nR}'×'
        printf "\n${nY}Please manually install the modules! ( pip install -r requirements.txt )${S}"
    fi
}

colors_set
python_install
venv_install
pip_update
modules_install

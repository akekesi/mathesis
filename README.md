# Mathesis (Videospiel)
<div align="center">

   [![Status](https://img.shields.io/badge/Status-in_progress-yellow.svg)](https://github.com/akekesi/mathesis?tab=readme-ov-file#description)
   <!-- [![CI](https://github.com/akekesi/mathesis/actions/workflows/ci.yml/badge.svg)](https://github.com/akekesi/mathesis/actions) -->
</div>

<div align="center">

   [![Python](https://img.shields.io/badge/Python-3.13.0-blue)](https://www.python.org/downloads/release/python-3130/)
</div>

<!-- <p align="center">
   <a href="#demo" title="Click to view full-size GIF in Demo section">
      <img src="gif/pelita_demo_50.gif" alt="pelita_demo_gif">
  </a>
</p> -->

## Table of Contents
1. [Description](#description)
1. [Demo](#demo)
1. [Python Installation](#python-installation)
1. [Python Environment Setup](#python-environment-setup)
1. [Pelita](#pelita)
1. [Authors](#authors)
1. [Acknowledgements](#acknowledgements)
1. [License](#license)

## Description
🚧 This project is a work in progress. Some features may be incomplete, untested, or lacking full documentation. 🚧  

This project was initially developed as an assignment for the [TU Berlin Mathesis (Videospiel) [WiSe 2024/25]](https://isis.tu-berlin.de/course/view.php?id=41051).

## Demo
<!-- <p align="center">
  <img src="gif/pelita_demo.gif" alt="pelita_demo_gif">
</p> -->

## Prerequisites
- [Python 3.13.0](https://www.python.org/downloads/release/python-3130/)
- [Pelita](https://github.com/ASPP/pelita_template)

## Python Installation
1. Install [Python 3.13.0](https://www.python.org/downloads/release/python-3130/), making sure to include Tcl/Tk during the installation process.
    - This will create the folder `C:\Program Files\Python313\tcl`, which contains the Tcl/Tk files that Pelita needs.

2. Fixing the Pelita Tcl/Tk Path Issue:
    - If you encounter the following error message:
        ```
        $ pelita
        Replay this game with --seed 7657247777183933888
        Using layout 'dead_ends_normal_713'
        TclError: Can't find a usable init.tcl in the following directories:
        {C:/Program Files/Python313/lib/tcl8.6} {C:/Program Files/lib/tcl8.6} C:/lib/tcl8.6 {C:/Program Files/library} C:/library C:/tcl8.6.14/library C:/tcl8.6.14/library

        This probably means that Tcl wasn't installed properly.
        . Exiting.`
        ```
    - Pelita looks for the tcl8.6 and tk8.6 folders in different locations. To fix this:
        - Copy the `tcl8.6` folder from `C:\Program Files\Python313\tcl\tcl8.6` to `C:\Program Files\lib\tcl8.6`.
        - Copy the `tk8.6` folder from `C:\Program Files\Python313\tcl\tk8.6` to `C:\Program Files\lib\tk8.6`.

## Python Environment Setup
### 1. Installing Python Packages
```
$ python -m pip install --upgrade pip
$ pip install -r requirements.txt
$ pip install -r requirements_dev.txt
```
## Pelita
### 1. Pelita User Guide
- [Pelita - pypi](https://pypi.org/project/pelita/)
- [Pelita - GitHub](https://github.com/ASPP/pelita_template)
- [Pelita - GitHub](https://git.tu-berlin.de/mathesis/pelitabots/)
### 2. Running Pelita
```
$ python pelita <player_1.py> <player_2.py>
```
- <player_1.py>: Script of player-1
- <player_1.py>: Script of player-2


## Authors
Attila Kékesi

## Acknowledgements
- [TU Berlin Mathesis (Videospiel) [WiSe 2024/25]](https://isis.tu-berlin.de/course/view.php?id=41051)
- [Pelita](https://github.com/ASPP/pelita_template)

## License
Code released under the [MIT License](https://github.com/akekesi/mathesis/blob/main/LICENSE).

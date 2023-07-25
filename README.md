# PiranhaGUI

PiranhaGUI is a piece of software designed to provide a graphical user interface for running DDNS analysis pipeline, [PIRANHA](https://github.com/polio-nanopore/piranha). PiranhaGUI currently can also optionally run [RAMPART](https://github.com/artic-network/rampart) It is being developed as part of the [Poliovirus Sequencing Consortium](https://polio-nanopore.github.io/). 
## Installation
PiranhaGUI may be installed on Mac, Windows or Linux, downloadable from the [releases](https://github.com/polio-nanopore/piranhaGUI/releases) page.
Installation instructions are on this page.

## Usage
Bugs and feature requests can be posted as 'issues' on [issue](https://github.com/polio-nanopore/piranhaGUI/issues).

### Startup
On startup you should see the following window:

<img src="./docs/Artifice_Startup_Screenshot.png">

This window shows you whether the required software is installed and whether they can be updated to the latest version.

- The first line of red text in this screenshot shows that docker is not running on this machine. If you see the same message the easiest way to solve it is to install [docker desktop](https://docs.docker.com/get-docker/) on your machine, launch it, and (once docker has lauched) restart piranhaGUI. The text should have updated to show that you have docker correctly installed. You will need start docker each time before you use piranhaGUI.

- Once you have docker ready to go, you can now pull the images for running RAMPART and PIRANHA from dockerhub by pressing the buttons provided. This requires an internet connection, the downloads at the time of writing are 200MB and 800MB respectively.

- From the startup screen you can also access the options menu by pressing the buttton labelled options. There are currenly two options available to modify. You can change the number of threads piranha will use for analysis, more threads will generally lead to faster results but increases the demand on your cpu, possibly slowing down other tasks. The default is half the number of threads available. You can also change the language from here, currently the options are french and english.

### Setting up run
Pressing the continue button will take you to the window to setup/edit your run, shown below:

<img src="./docs/Artifice_Edit_Run_Screenshot.png" width="650">

- There are three fields to fill here, you can browse your OS file system for each them or simply copy in a path if you have it to hand. 
- The first is samples, this is should be a csv file with at least two columns, matching each to sample to the corresponding barcode on each row. The first row should contain labels for eah column. Once you have selected your samples file you may want to view them with the provided button. This will open a window where you can select the column specifying the barcode and sample id, based on the label at the top of each column. 
- The second field to fill is the MinKnow run folder. This should be the folder containing the demultiplexed samples outputed by MinKnow. 
- Lastly the output folder field specifies where PIRANHA will place its' report files.

### Running Analysis
Once the run has been setup pressing continue will take you to the window for actually running RAMPART and PIRANHA analysis, shown below:

<img src="./docs/Artifice_Execute_Screenshot.png">

- The first button will take you back to the previous window if you need to modify your run. 
- Below there is an indicator for whether RAMPART is running, and what protocol is selected. There is also button for selected another protocol for RAMPART which will open a window for this purpose. piranhaGUI comes with two protcols to choose from, the ARTIC poliovirus protocol and the default RAMPART protocol. You can also add your own protocols if needed. 
- Next there is button for starting RAMPART, if RAMPART is currently running there is also a button for viewing it in browser. There is a similar text indicator and button for running PIRANHA analysis. If PIRANHA has finished creating a report there will also be a button to view it in browser. There is also a button for configuring options specific to PIRANHA. Finally there are two tabs for selecting whether to view the text output either RAMPART or PIRANHA

# Artifice

Artifice is a piece of software designed to provide a graphical user interface for running bioinformatics tools. It is being developed as part of the [Poliovirus Sequencing Consortium](https://polio-nanopore.github.io/). Currently there are two versions of Artifice in development: the base version which runs only [RAMPART](https://github.com/artic-network/rampart), and PiranhaGUI which runs both RAMPART and [PIRANHA](https://github.com/polio-nanopore/piranha).

## Usage
As a GUI tool Artifice is intended to be intituitive to use but a guide is provided below nonetheless. If you find some element of the software's design particularly confusing, feel free to create an [issue](https://github.com/CorwinAnsley/artifice/issues) on this repository.

On startup you should see the following window:

<img src="./docs/Artifice_Startup_Screenshot.png">

The first line in this screenshot indicates docker is not running on this machine. If you see the same message the easiest way to resolve it is to install [docker desktop](https://docs.docker.com/get-docker/) on your machine, launch it, and restart Artifice. The text should have updated to indicate you have docker correctly installed.

Assuming you have docker ready to go, you can now pull the images for running RAMPART and PIRANHA from dockerhub by pressing the buttons provided. This requires an internet connection, the downloads at the time of writing are 200MB and 800MB respectively, so they shouldn't take too long even on a relatively slow connection.

From the startup screen you can also access the options menu, shown below, by pressing the buttton labelled options. There are currenly two options available to modify. You can change the number of threads piranha will use for analysis, more threads will generally lead to faster results but increases the demand on your cpu. The default is half the number of threads available. You can also change the language from here, currently the options are french and english.

Pressing the continue button will take you to the window to setup/edit your run, shown below:

T

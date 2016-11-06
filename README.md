# ALFIX #

Alfix is an [open-source](COPYING.md) web-based viewer for the eLearn
workshop manuals for various Alfa Romeo, Lancia and Fiat cars.

## Software requirements ##

This section lists the external software dependencies of this project.

First of all, you will need an eLearn CD or an image of of one.
eLearn is proprietary software which you need to purchase yourself,
don't ask me for a copy or help on finding one. At the moment only
Alfa 156 eLearn has been tested. In theory others should work too
but see the section on bugs, todo etc.

The rest is free software like Alfix. The versions noted in parentheses
reflect what was used and tested during development on Fedora Linux.
Other versions might work just as well or even better. Or not.

### Setup ###

Software required only during setup:

* mdbtools  (>= 0.7.1)
* innoextract (>= 1.6)
* dos2unix (>= 7.3.3)

### Running ###

Software required for running the application server:

* python 3 (>= 3.5.1)
* lxml (>= 3.4.4)
* sqlite (>= 3.13.0)

### Viewing ###

As Alfix is basically a custom web server for the eLearn content,
it is technically possible to run it on a headless server and browse the
contents on any arbitrary web client, including tablets, mobile phones,
text-only clients and whatnot. At the moment it has been only tested
with Firefox running on local computer so for anything else YMMV,
and you'd have to modify the source to try it.

* a modern web browser (firefox >= 49)

Do not expose Alfix to the public internet! It is not written 
be secure in any way, and almost certainly you have no permission to
share the eLearn content to anybody else.

## Installation ##

### Installing dependencies (Fedora)
On Fedora (>= 24) installing this should ensure you have everything
needed to setup and run the software:

    # dnf install python3-lxml innoextract mdbtools sqlite dos2unix firefox

### Installing Alfix

Replace `<path-to-cd>` with the path your CD or iso-image is mounted.
For example, by default Fedora 24 mounts Alfa 156 eLearn CD at
`"/run/media/${USER}/Alfa Romeo 156"`

    $ git clone https://gitlab.com/pmatilai/alfix.git
    $ cd alfix
    $ ./setup.sh <path-to-cd>

The setup script will copy all the relevant content from the CD to
the Alfix directory so the CD (or image) does not need to remain mounted
after the initial setup.

## Running ##

Once the setup has successfully completed (mind you it is not very
error tolerant at this point), running the software is simply:

    $ ./alfix.py

On startup it prints its address on standard output, which by default is
http://localhost:8080/ - point your browser there and enjoy.

## Bugs, todo and all ##

Bear in mind this is a very early version of the software and
will have any number of bugs, unimplemented features and other rough
edges. 

It should not eat your data, kids or pets but do NOT blindly trust
the information you get from it, there are various unimplemented
features at the moment which might result in incorrect information
shown in some points. And of course there might be other bugs.
And finally, at best Alfix can only be as correct as the source data
on eLearn. There are bugs, typos and other mistakes in it too.

Some known issues and future plans are listed in the project [TODO](TODO.md).
Bug reports and other feature requests on the GitLab issue tracker are
welcome, just keep in mind this is a hobby project done on my scarce
free time and resources.

## Authors

* Panu Matilainen <pmatilai@laiskiainen.org>


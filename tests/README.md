# Unit Testing in PyCord
## Scope
Currently, only the internal framework can be unit tested, but plans are in place
for testing your applications
## Setup
First install all requirements from the requirements.txt file in this directory
### On GNU/Linux systems
The testing system uses GNU make as the interface, if you use the GNU coreutils,
make is likely already there, if not, consult your distro's documentation to get it

In order to read the data of requests, you must generate some key files for the proxy,
you can do this by running `make gencerts`
### On Windows systems
A powershell script is in the works, but for now only a Makefile is available
## Running Tests
Execute the command `make runtests` to run the tests


# Server side scripts
## Description.
Collection of scripts that connect Suserium components.  Primarliy run on the server, except for new chain client.

## New chain

Called from gitApiInterface.py when Suserium is added to a github repo.  This creates a new chain within a hidden folder (~/.sawtooth_projects/PrjName_prjID).
Noteable files in the hidden folder include: etc/.ports, etc/.suse.

This scripts starts up the validator, rest-api, and the handlers for each family protocol (e.g. health, suse, settings).  Each project requiers 3 ports.

A file in /opt/lamp/htdocs/connnect/ is also created containing the default ".suse" configurations and the ports.  This is later passed to new chain client by the user.

Creates a file in the map folder linking the repo id and the ports the chain should run on.  Used for persistance.


## New chain client
From the client's GUI, this script is passed the url in the .suse file to connect to the project's chain.

## Commit handler
Called from gitApiInterface.py when a Suserium repo pushes a new commit.

## Proposal listener
Used the handle proposal periods for each project

## Install
Used to set up and install Suserium client

## Startup
Server will call this script upon startup to start all the processes for each chain.

## Die all
Delete all Suserium related data and procesess.


# GitHub API Interface
Susereum is a GitHub App and will be soon published to the GitHub marketplace. As a GitHub App it has permissions to listen to certain events on whatever project repository has installed the app. The GitHub API Interface is responsible for allowing Susereum to communicate with GitHub.

## Git API
The main purpose of the interface is to listen to Git API webhook events such as when Susereum is installed on a project, with push events, etc.

The interface also is able to edit the repository. When Susereum is installed on a project, the GitHub API Interface creates a .suse file in the main directory of the project repo with the default configuration for code smells. It also updates the .suse file whenver new code smell configurations are proposed and passed using the GUI.

For editing the repository, the interface must authenticate itself by passing a token in the header. To generate the token, this script requires Susereum's private-key.pem, GitHub App Identifier, and GitHub Webhook Secret.

## Smee Proxy
Susereum uses a smee proxy that listens to the webhook events, and forwards them to the Susereum server's 3000 port. Then, the GitHub API Interface is listening on port 3000.

## Communication with Susereum
The GitHub API Interface communicates with Susereum by sending event information to Central Server Scripts. This repository requires new_chain_command and push_command files that formulate the command to run the Central Server Scripts. 

## Running The Interface
1. Download the private-key.pem and take note of the GitHub APP ID from Susereum's GitHub App Settings
2. Ask for the webhook secret and the commands to call Central Server Script from Susereum's lead developers
3. Start the smee proxy
`smee -u https://smee.io/XviEAcJZCaJ9jnW`
4. Export the environment variables
`export GITHUB_APP_IDENTIFIER=<ID>`
`export GITHUB_WEBHOOK_SECRET="<secret>"`
``export GITHUB_PRIVATE_KEY=`awk '{printf "%s\\n", $0}' private-key.pem` ``
5. Start the GitHub API Interface
`python gitApiInterface.py 3000`

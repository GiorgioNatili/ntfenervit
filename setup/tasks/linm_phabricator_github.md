Configuring Phabricator with Github
===================================

 1. Starting from http://projects.gnstudio.biz/
 2. Click on "Diffusion" tab
 3. Click on + "New Repository"
 4. Choose "Import an Existing External Repository", click Continue
 5. Choose "Git" and click Continue
 6. Enter:
    * "Choose a human-readable name for this repository": Ntfenervit Github Repository
    * "Choose a "Callsign" for the repository": G
 7. Enter "git@github.com:GiorgioNatili/ntfenervit.git" for "Repository Remote URI"
 8. Choosing "K1 Migrated Repository Credential (BBITALY)" SSH Key for "Authentication"
 9. In Policies, kept the default, which is:
    * Visible To: "All Users"
    * Editable By: "Administrators"
10. Under "Repository Ready!", choose "Configure More Options First"

## Edit Repository

Edit Ntfenervit Github Repository
1. Click on "Activate Repository"
2. Wait for "Status" to say "Fully Imported"


## Notes:
The repo is not integrated to Phabricator but couldn't find a way to associate a commit to a task.

## Git Diff Log Analyser

- Details
Using the ctags tool, the methods and variables in the diff file are interpreted, then based on the changed lines, the method of the change is inferred and eventually the list of methods changed in one commit, the owner to which they belong, the date, and the version number of the current build (not required) is uploaded to the database via a restapi service provided by another directory.
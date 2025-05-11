@echo off
REM This script adds a contributor to the repository history
REM Usage: add_contributor.bat ContributorName contributor@email.com

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set CONTRIBUTOR_NAME=%~1
set CONTRIBUTOR_EMAIL=%~2

REM Create a temporary commit to add the contributor
echo # Adding %CONTRIBUTOR_NAME% as a contributor > temp_contributor.md
git add temp_contributor.md
git config --local user.name %CONTRIBUTOR_NAME%
git config --local user.email %CONTRIBUTOR_EMAIL%
git commit -m "Adding %CONTRIBUTOR_NAME% as a contributor"
git rm temp_contributor.md
git commit -m "Cleanup temporary file"

REM Reset to original user
git config --local --unset user.name
git config --local --unset user.email

echo Contributor %CONTRIBUTOR_NAME% has been added to the repository history.
echo Don't forget to push the changes with: git push origin main
goto :eof

:usage
echo Usage: %0 ContributorName contributor@email.com
exit /B 1
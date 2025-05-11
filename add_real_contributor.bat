@echo off
REM This script adds a real GitHub contributor to the repository history
REM Usage: add_real_contributor.bat GithubUsername "Real Name" email@example.com

if "%~1"=="" goto usage
if "%~2"=="" goto usage
if "%~3"=="" goto usage

set GITHUB_USERNAME=%~1
set CONTRIBUTOR_NAME=%~2
set CONTRIBUTOR_EMAIL=%~3

REM Create a temporary commit with proper GitHub username
echo # Adding %GITHUB_USERNAME% as a contributor > temp_contributor.md
git add temp_contributor.md
git config --local user.name "%CONTRIBUTOR_NAME%"
git config --local user.email "%CONTRIBUTOR_EMAIL%"
git commit --author="%CONTRIBUTOR_NAME% <%CONTRIBUTOR_EMAIL%>" -m "Adding %GITHUB_USERNAME% as a contributor"
git rm temp_contributor.md
git commit --author="%CONTRIBUTOR_NAME% <%CONTRIBUTOR_EMAIL%>" -m "Cleanup temporary file"

REM Reset to original user
git config --local --unset user.name
git config --local --unset user.email

echo Contributor %GITHUB_USERNAME% has been added to the repository history.
echo Don't forget to push the changes with: git push origin main
goto :eof

:usage
echo Usage: %0 GithubUsername "Real Name" email@example.com
exit /B 1
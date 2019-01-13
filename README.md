# KattisScraper
Scrapes some data from open.kattis.org of a user's completed problems.

**WIP**

Currently outputs data to a csv file formatted:

    problem name, problem link, problem difficulty, submission date, submission language, submission code
    
Limitation: works as of 12 Jan 2019, if site changes too much it may break

Others:

* only grabs latest successful submissions regardless of different submissions
* doesn't have much in terms of error checking, so probably prone to crashing such as invalid login, networking issues, etc.
* takes a while to collect all the data, usually in navigating pages (takes about 2.5 minutes with ~130 solutions)

# Goals:
 - periodically query running processes and track the lifetimes of particular processes corresponding to applications
 - DONE categorize those particular processes (and corresponding applications) as work, leisure, common, or other
 - *1 aggregate the wall time per day spent on work, leisure, or browser applications
 - send out email notifications summarizing the aggregation

# Solutions:
 - schedule scraping of running processes
 - DONE compare new scrape against previous scrape to see if/which processes have stopped running, i.e., the application has closed. Cases:
   - DONE The process (same PID, ctime) is still alive and running
   - DONE The process is not running but has not been reassigned
   - DONE The process is now running but with a different ctime, i.e., it has stopped and been reassigned

# *1
 - script runs periodically, so nothing is kept in memory between executions --> object-based storage will not work
 - each script execution should run a "scrape" --> get running applications and write to a database
 - **database tables based on daily usage --> one per day**
 - check existing application entries in table against current scrape (using Application functions)
 - **how to treat separate executions and closings of applications? --> don't categorize applications by .exe, but by execution

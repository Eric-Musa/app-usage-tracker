# Goals:
 - periodically query running processes and track the lifetimes of particular processes corresponding to applications
 - categorize those particular processes (and corresponding applications) as work, leisure, browser, or other
 - aggregate the wall time per day spent on work, leisure, or browser applications
 - send out email notifications summarizing the aggregation

# Solutions:
 - schedule scraping of running processes
 - DONE compare new scrape against previous scrape to see if/which processes have stopped running, i.e., the application has closed. Cases:
   - The process (same PID, ctime) is still alive and running
   - The process is not running but has not been reassigned
   - The process is now running but with a different ctime, i.e., it has stopped and been reassigned
 -

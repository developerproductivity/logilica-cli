# logilica-weekly-report

This project exports Logilica data to add it to a weekly report. 

The data is obtained from team dashbaords, one dashboard per team. The list of dashboards is stored in the team_dashbaords.txt file. As teams are onboarded a new team dashboard is created in Logilica and the team_dashboards.txt file is updated with the new team's dashboard name.

The download_pdf.py script uses Playwright, see https://playwright.dev/python/docs/intro for instructions to install Playwright. 

To run the script run `pytest download_pdfs.py`. To run in debug mode run `PWDEBUG=1 pytest download_pdfs.py`. For mode details on runnin and debugging see https://playwright.dev/python/docs/running-tests.

The downloaded PDF files are stored in the `downloaded_pdfs` directory. 

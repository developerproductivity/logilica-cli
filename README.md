# logilica-weekly-report

This project exports Logilica data to add it to a weekly report. 

Environment variables must be set for LOGILICA_DOMAIN, LOGILICA_EMAIL, and
LOGILICA_PASSWORD, the corresponding values can be obtained from Bitwarden.

The data is obtained from team dashboards, one dashboard per team. Teams data 
is stored in the weekly_report.yaml file. 

When a new team is onboarded, a new dashboard should be created for it, and the 
weekly_report.yaml file is updated accordingly.

The download_pdf.py script uses Playwright, to setup your environmemt you can 
run `pip install -r requirements.txt` 

To run the script run `python3 download_pdfs.py`. To run in debug mode run 
`PWDEBUG=1 python3 download_pdfs.py`. For mode details on running and debugging 
see https://playwright.dev/python/docs/running-tests.

The downloaded PDF files are stored in the `downloaded_pdfs` directory. 

When a new team is onboarded, a new dashboard should be created for it, and 
the dashboard name should be added to the file.

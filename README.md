# DenagoReports

## Getting Started
To generate reports, download `generate-reports.py`
as well as the .txt files containing the SuiteQL 
queries that are prewritten to provide the correct 
data, and `requirements.txt`. Also make sure that 
Python is installed,along with the correct libraries. 
(More on this later).

## Generating Data Sets
To generate the data sets, paste the two SuiteQL 
queries into the SuiteQL Query Tool in NetSuite. One
can also run a query via the NetSuite API. 
Paste the generated tables into separate .csv files
titled `UPS-Shipments_L30D.csv` and 
`LTL-Shipments_L30D.csv` repectively. Once these files
are updated, you are ready to generate the reports.
Ensure that any of the date columns are formatted as
date with the following format: `yyyy-mm-dd`.
All other cells should be formatted as text. Save the 
file as a `.csv`.

### Important
The files **__must__** be titled as above, or the file
names changed with the script by editing the variables 
```    
    uinputFile = 'UPS-Shipments_L30D.csv'
    linputFile = 'LTL-Shipments_L30D.csv'
```
Failure to do so will result in an error.

## Generating Reports
To run the script and generate the reports, run 
the following command in the directory that 
the script is stored:
`py generate-reports.py`

### Valid Arguments for Execution
The following arguments can be appended in order
change the functionality of the script:
```
-u / --upsonly (generates only reports for UPS Ground)
-l / --ltlonly (generates only reports for LTL shipments)
-s / --show (shows windows for the plots that are generated
             after they are created. Otherwise will only 
             .pdf's of the figures)
-h (shows quick help for valid input args)
```

## Results
The script will create two directories UPS & LTL. These will
store the resulting .pdf's for the generated plots, as well 
as a .txt file detailing various aspects of the shipments
contained in the data sets.

## Installing Packages
To install the required packages, simply run the following command
in the terminal `pip install -r requirements.txt`. This will install
all of the required libraries to run the script. If pip is not 
installed, refer to this link: https://pip.pypa.io/en/stable/installation/
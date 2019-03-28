# duplicati-file-history

This script displays history of changes (file addition, removal, modification) of an individual file within an entire history of [duplicati](https://github.com/duplicati/duplicati/) backup.

## Requirements

* `duplicati-cli` (tested in linux only)

## Usage

`dfh.py  <path to duplicati backup>  <path to duplicati database>  <filter of path(s) to find, might contain "?" or "*">`

e.g.:

`dfh.py  "/mnt/hdd0/backup"  "/home/duplicati.sqlite"  "*2019-03-monthly-report.docx"`

output:

```
getting backup info...
    found version ranges: [0, 20]
counting files...
    1 file(s) found:
        /home/nagimov/docs/reports/monthly-operational-reports/2019-03-monthly-report.docx
getting backup revisions...
    21 backup revisions found
checking file revision changes...
    added versions:
        19      : 3/10/2019 1:00:07 AM 47.15 KB
    modified versions:
        18      : 3/11/2019 1:00:08 AM 100.75 KB
        11      : 3/18/2019 1:00:08 AM 146.36 KB
```

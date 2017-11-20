# Crawling [vgchartz.com](www.vgchartz.com)

They collect all weekly sales data for all regions as recorded on the website.

Additionally, the script will try to draw a plot of aggregate weekly sales data using `matplotlib`. If your environment does not allow for a display, I suggest that you copy and paste the scripts (this is a small project) to a Jupyter notebook and add the following line in the first line:

```
%matplotlib inline
```

It is a ipython magic that allows the notebook to draw plots in the output cell.

Without a display, the script will _not_ work.

==============================================================================

## Installation
### Via pip
Please install all the modules listed in requirements.txt. You can do so
with a following command in the terminal:

```bash
$ pip intall -r requirements.txt
```

If the default Python version is NOT 3.x on your machine, you may want to use
pip3 instead of pip.

### Manual
If you get any ImportError while running the modules, you may want to install
the following modules manually (They are all installabe via pip):

  * BeautifulSoup
  * pandas
  * requests
  * sqlalchemy
  * mysqlclient

If you get an `ImportError` regarding `MySQLdb`, it means that `sqlalchemy` can't find the driver. On Ubuntu 16.04, you may try the following:

```bash
$ sudo apt-get install python-mysql
```

The script currently does not support any other drivers.

## Execution
Once you have set up the working environment, please run main.py.

## Output files
All output files will be located in release/output. I have included a sample data of USA 
as a reference.

The CSV files are organized by region. Within each file is aggregate weekly data for that region.

## MySQL database
Currently, all collected data are saved on my EC2 instance. To access the database, use the following crednetials:

  * Username: guest
  * IP: 54.198.181.165
  * Database name: vgchartz


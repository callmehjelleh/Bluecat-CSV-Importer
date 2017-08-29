import pandas as pd

# <summary>
# pandas DataFrame interface for easily parsing csv files
# </summary>
# <todo priority="high">
# Add write abilities
# </todo>
# <todo priority="low"
# Rename it to CSV_IO or something logical for read/write. Or Create a CSVWriter class
# </todo>
class CSVReader:

    # <summary>
    # constructor for CSVReader class
    # </summary>
    # <param name="file" type="string">
    # path to csv file to parse
    # </param>
    # <param name="callback" type="function">
    # callback function for error reporting
    # </param>
    def __init__(self, file, callback=None):
        self.file = file
        self.reader = pd.read_csv(file)
        if callback:
            self.callback = callback
        else:
            self.callback = self.default_callback

    # <summary>
    # returns a list of pandas.core.series.Series instances, for each row
    # </summary>
    def getRows(self):
        return [i for i in self.reader.iterrows()]

    # <summary>
    # returns a list containing a pandas.core.series.Series instance, based on the name field
    # </summary>
    # <param name="name" type="string">
    # The name of the column to grab
    # </param>
    # TODO: Convert name to 'names' and list format to allow multiple cols at a time.
    # TODO: Find out how to use strings as indexes. e.g. getColumns(['Name', 'IP Address'])['IP Address'] = ['192.168.0.1', ...]
    def getColumn(self, name):
        try:
            return [i[1][name] for i in self.getRows()]
        except:
            self.callback('No field called %s' % name, False)

    # <summary>
    # Similar to getColumn, but takes a list of names and returns a dict of columns
    # </summary>
    # <param name="names" type="list">
    # The list of names to retrieve from the CSV
    # </param>
    def getColumns(self, names):
        try:
            cols = {}
            for name in names:
                cols[name] = [i[1][name] for i in self.getRows()]
            return cols
        except:
            self.callback('No field called %s' % name, False)

    # <summary>
    # Allows modification of data in the DataFrame structure created by the pandas module (in memory csv basically)
    # </summary>
    # <param name="column_name" type="string">
    # The name of the column to modify (e.g. "Name", "IP", etc.)
    # </param>
    # <param name="index" type="int">
    # The index within the column to be changed
    # </param>
    # <param name="value" type="string">
    # Value to which the value at [column_name, index] should be set
    # </param>
    # <todo priority="low">
    # Either use this or remove it. It was from an old design choice and is currently unused.
    # </todo>
    def modifyValue(self, column_name, index, value):
        try:
            self.reader.set_value(index, column_name, value)
            return self.getColumns(column_name)[1][index] == value
        except Exception, e:
            self.callback("%d" % self.reader.index, False)
            self.callback("Could not set value in DataFrame: %s" % e, False)

    # <summary>
    # Removes rows from the DataFrame structure
    # </summary>
    # <param name="indexes" type="list">
    # The list of row indexes to remove from the DataFrame
    # </param>
    # <todo priority="low">
    # Either use this or remove it. It was from an old design choice and is currently unused.
    # </todo>
    def removeRows(self, indexes):
        self.reader = self.reader.drop(indexes)

    # <summary>
    # The default callback (in case one isnt provided.)
    # This really should not be necessary
    # </summary>
    # <param name="msg" type="string">
    # The error message
    # </param>
    # <param name="fail" type="boolean">
    # Did the program fail? controls whether to exit after the callback
    # </param>
    @staticmethod
    def defaultCallback(msg, fail):
        print msg
        if fail:
            exit(-1)

if __name__ == '__main__':
    csv = CSVReader('testdevice.csv')

    assert(csv.getColumns('Not existing') == None)
    assert(csv.getColumns('Name'))
    assert(type(csv.getColumns('Name')) == dict)
    assert(type(csv.getRows()) == list)
    assert(type(csv.getRows()[1]) == pandas.series.Series)

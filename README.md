# Proteus

## Quick-Start

To run the module simply run the main module:
```
python __main__.py
```

## Easily import CSV's to Bluecat Address Manager

Proteus allows users to simplify the task of importing data into Bluecat Address Manager by simply providing a CSV to the module, and letting it do the heavy lifting!


## Code Standards

### IF YOU INTEND TO WORK ON THIS PLEASE READ

Proteus pull requests will be denied if code standards are not met. Here we'll discuss the important parts of these code standards.

### Classes 

- Proteus makes extensive use of python's mediocre attempt at Object-Oriented Programming. Only one class should be contained per module

- Classes should be named in a clear and concise way based on what they are doing (e.g. AddressValidator is for validating IP Addresses, BAMClient is the API client for the BAM service, CSVReader reads and parses csv files, etc.)

- Class naming conventions are PascalCase and never snake\_case or camelCase. This helps to differentiate classes from variables, etc.

- Classes should be named the same as their parent module

- Accessors should be named the same as the variable (e.g. accessor for class.\_\_name or class.name would be called as class.name())

- Constructor should always be the first function present at the top of the class

### Variables

- variables should be snake\_case

- Name them something clear and concise but use full words (e.g. address not addr, password not passwd, etc.)

- global variables are bad. Don't use them. Favor member and local variables

### Functions

- Use camelCase for public methods and functions

- Use snake\_case for private methods

### Logging

- Do not use the root logger. Each module should have it's own logger.

- For the most part, tracking runtime information should use logger.debug

- logger.critical should only be used if the application must abort, otherwise favor logger.error or logger.warning

### Modules

- Name them something obvious. That's about it

### Documentation

#### THIS IS *VERY* IMPORTANT

- Use detailed but concise git commit messages (e.g. "Implemented creation of IPv4 networks to BAMClient class", NOT "implemented some new features")

- Every class and every function should have detailed descriptions. XML tags are used to make searching easier. Here's a list of valid tags along with their params:

	- \<summary\>
	- \<param\>
		- name (*string*)
		- type (*string*)
	- \<todo\>
		- priority (*specified string*)
			- high
			- moderate
			- low

### Testing

#### ALSO *VERY* IMPORTANT

- Eventually, all commits will require associated tests. These tests should be run when a module is run as main. This can be achieved using the following format for each module:

```python
if __name__ == "__main__":	
    # Tests go here
```

- Make sure your code actually works before committing it. Seriously. Write the tests. If there's no tests associated I'm rejecting the commit until tests are provided.

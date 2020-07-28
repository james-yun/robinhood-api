# robinhood-api
[![PyPI version](https://badge.fury.io/py/robinhood-api.svg)](https://badge.fury.io/py/robinhood-api)
![Publish to PyPI workflow](https://github.com/james-yun/robinhood/workflows/Publish%20to%20PyPI%20workflow/badge.svg)

the unofficial Robinhood API (pre-alpha)

## Installation

```bash
pip install robinhood-api
```

## Authentication
The first time you log in, you will be prompted to verify your identity by entering a code send to your phone or email. 
This will generate an OAuth bearer token that will be stored in tokens.json. 
Subsequent logins will not require your credentials.

## Usage

```python
import robinhood


# you will be prompted for your username and password
robinhood.login()  

# check your stocks
print(robinhood.positions())
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](LICENSE)

# robinhood
the unofficial Robinhood API (pre-alpha)

## Installation

```bash
git clone https://github.com/james-yun/robinhood.git
cd robinhood
python3 example.py
```
I hope to publish to the [pip](https://pip.pypa.io/en/stable/) package manager once this production ready.

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

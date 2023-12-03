# VOIP REST

## PRE-REQS

To use the AWS apis, please make a .env file with the following fields

```commandline
AWS_ACCESS_KEY_ID=<ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<SECRET_ACCESS_KEY>
AWS_DEFAULT_REGION=us-east-1
```

## SETUP

### Use python 3.8.17

```commandline
pip install -r requirements.txt
```

### To test

Run all tests

```commandline
pytest tests/e2e/
```

Run specific tests

```commandline
# To run a specific test file:
pytest tests/e2e/test_machine_setup.py

# To run a specific test function within a file:
pytest tests/e2e/test_machine_setup.py::test_setup_machine
```

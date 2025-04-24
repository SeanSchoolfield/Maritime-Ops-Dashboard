import kafka_service.consumer
import pytest

"""
// TODO
- Items to test
    - Fast API websocket
    - Simulate with periodic GET/POST requests

# EEZ issue
- Handles large objects being retrieved from

# Typical shit
- Interprets invalid requests/data, and addresses it to client properly
    - Necessary data is parsed
- Handles DBOperator timeouts and errors
    - Properly passes on other backend errors to client for unintended failures
    - Need-to-know
    - performs operator.rollback() when necessary
- All connections are closed()

"""
if __name__ == "__main__":
    print("Websocket testing IN PROGRESS")

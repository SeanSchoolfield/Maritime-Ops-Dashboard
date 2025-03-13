import kafka_service.consumer
import pytest

"""
// TODO
- Items to test
    - Kafa Consumer script

    - Simulate with periodic pulls from database for various topics

- Things to test for
    - handles pagination and offset of mass topic messages
    - Each consumer in the group handles its own topic
    - Consumer is capable of determining most recent event, update, or change 
        - works backwards from there (historical)
    - Properly handles connection error
        - provides necessary data for client
        - displays necessary details to console
    - Properly handles missing data or un-updated data
"""
if __name__ == "__main__":
    print("Consumer Tester IN PROGRESS")

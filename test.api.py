import pytest

"""
// TODO
- Items to test:
    - gfw_api.py
    - weather_api.py
    - coop_api.py

- Things to test for
    - Make sure that invalid queries throw a response to console and doesn't push to Kafa/DB
    - iterates through pagination sequentially
    - calls query() for data that updates based on id provided
        - If no data varies, do not call modify(), and do not push to topic
        - If no data is returned, call add(), and push to topic
        - If variants occur, call modify() on varied data, and push to topic
    - ???
    - Profit
"""
if __name__ == "__main__":
    print("API tester IN PROGRESS")

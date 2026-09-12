from react_agent.agent import add, current_utc_time


def test_add_tool():
    assert add.invoke({"a": 2, "b": 3}) == 5


def test_current_utc_time_tool():
    result = current_utc_time.invoke({})
    assert isinstance(result, str) and result.endswith("+00:00")

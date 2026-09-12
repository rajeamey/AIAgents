from agent_template.agent import add


def test_add_tool():
    assert add.invoke({"a": 2, "b": 3}) == 5

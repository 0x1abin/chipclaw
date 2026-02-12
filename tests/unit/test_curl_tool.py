"""
Unit tests for chipclaw.agent.tools.curl module
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chipclaw.agent.tools.curl import CurlTool


def test_curl_tool_creation():
    """Test CurlTool instantiation and attributes"""
    tool = CurlTool()
    assert tool.name == "curl"
    assert "HTTP" in tool.description or "curl" in tool.description
    assert "url" in tool.parameters["properties"]
    assert "method" in tool.parameters["properties"]
    assert "headers" in tool.parameters["properties"]
    assert "data" in tool.parameters["properties"]
    assert tool.parameters["required"] == ["url"]


def test_curl_tool_schema():
    """Test OpenAI function calling schema generation"""
    tool = CurlTool()
    schema = tool.to_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "curl"
    assert "parameters" in schema["function"]
    assert "properties" in schema["function"]["parameters"]


def test_curl_tool_default_method():
    """Test that default method is GET"""
    tool = CurlTool()
    # Mock a request to a non-existent host to verify error handling
    result = tool.execute(url="http://localhost:99999/nonexistent")
    # Should return an error string, not raise an exception
    assert isinstance(result, str)
    assert "Error" in result or "HTTP" in result


def test_curl_tool_unsupported_method():
    """Test unsupported HTTP method returns error"""
    tool = CurlTool()
    result = tool.execute(url="http://example.com", method="OPTIONS")
    assert "Error" in result
    assert "Unsupported" in result


def test_curl_tool_method_case_insensitive():
    """Test that method parameter is case-insensitive"""
    tool = CurlTool()
    # Lowercase should be normalized to uppercase
    result = tool.execute(url="http://localhost:99999/nonexistent", method="get")
    # Should not fail with "Unsupported method" error
    assert "Unsupported" not in result


def test_curl_tool_parameters_enum():
    """Test that method parameter has correct enum values"""
    tool = CurlTool()
    method_prop = tool.parameters["properties"]["method"]
    assert "enum" in method_prop
    expected = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    assert method_prop["enum"] == expected


def test_curl_tool_with_headers_param():
    """Test that headers parameter is defined correctly"""
    tool = CurlTool()
    headers_prop = tool.parameters["properties"]["headers"]
    assert headers_prop["type"] == "object"


def test_curl_tool_with_data_param():
    """Test that data parameter is defined correctly"""
    tool = CurlTool()
    data_prop = tool.parameters["properties"]["data"]
    assert data_prop["type"] == "string"


def test_curl_tool_error_handling():
    """Test that connection errors return error strings"""
    tool = CurlTool()
    result = tool.execute(url="http://localhost:99999/invalid", method="POST", data='{"key":"value"}')
    assert isinstance(result, str)
    assert "Error" in result


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])

from locateanything.core import locate, TOOL_NAME
def test_no_model(tmp_path):
    p = tmp_path / "x.jpg"; p.write_bytes(b"\xff\xd8\xff\xe0notarealjpeg")
    res = locate(str(p))
    assert res["tool"] == TOOL_NAME and "candidates" in res

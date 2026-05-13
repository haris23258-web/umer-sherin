httpx.ConnectError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/umer-sherin/stramlit.py", line 36, in <module>
    inv_count = supabase.table("inventory").select("*", count="exact").execute()
File "/home/adminuser/venv/lib/python3.14/site-packages/postgrest/_sync/request_builder.py", line 90, in execute
    r = send_with_retry(self.request)
File "/home/adminuser/venv/lib/python3.14/site-packages/postgrest/_sync/request_builder.py", line 51, in send_with_retry
    resp = req.send(headers)
File "/home/adminuser/venv/lib/python3.14/site-packages/postgrest/base_request_builder.py", line 90, in send
    return self.session.request(
           ~~~~~~~~~~~~~~~~~~~~^
        self.http_method,
        ^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        auth=self.auth,
        ^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_client.py", line 825, in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_client.py", line 914, in send
    response = self._send_handling_auth(
        request,
    ...<2 lines>...
        history=[],
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_client.py", line 942, in _send_handling_auth
    response = self._send_handling_redirects(
        request,
        follow_redirects=follow_redirects,
        history=history,
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_client.py", line 979, in _send_handling_redirects
    response = self._send_single_request(request)
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_client.py", line 1014, in _send_single_request
    response = transport.handle_request(request)
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_transports/default.py", line 249, in handle_request
    with map_httpcore_exceptions():
         ~~~~~~~~~~~~~~~~~~~~~~~^^
File "/usr/local/lib/python3.14/contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/httpx/_transports/default.py", line 118, in map_httpcore_exceptions
    raise mapped_exc(message) from exc

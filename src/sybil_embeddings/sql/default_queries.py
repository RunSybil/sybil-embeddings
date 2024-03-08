EVERYTHING_QUERY =  """
SELECT 
    a.id as request_id,
    a.request_target as request_target,
    json_extract(a.data, "$.http_request.http_method") as request_method,
    json_extract(b.data, '$.http_request.base64_body') as request_body,
    json_extract(b.data, '$.http_response.base64_body') as response_body,
    json_extract(a.data, '$.http_request.headers') as request_headers,
    json_extract(b.data, '$.http_response.headers') as response_headers
    -- a.id as request_id, 
    -- a.event as request_event, 
    -- a.data as request_data, 
    -- a.*,
    -- b.id as response_id, 
    -- b.event as response_event, 
    -- b.data as response_data,
    -- b.*
 FROM (
    SELECT e.*, 
        json_extract(e.data, '$.http_request.request_target') as request_target 
    from events as e 
    where event_type == 'HttpProxyRequest'
    ) as a
 JOIN (
    SELECT * from events where event_type == 'HttpProxyResponse'
    ) as b 
 ON json_extract(a.data, '$.pair_id') == json_extract(b.data, '$.pair_id') 
where (
        (response_body != "" and response_body is not null) 
        or 
        (request_body != "" and request_body is not null)
    )
;
"""
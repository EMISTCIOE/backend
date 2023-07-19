# TCIOE API

**_ Search Endpoints _**

## Staffs

Endpoint : /api/department/staffs/search/?name=xxx&designation=xxx&department=xxx&key_officials=xxx

- All params are optional, just pass the parameter as required for search.
- If no params are passed, all staffs will be returned.
- key_officials can be either true or false.

## Subjects

Endpoint : /api/department/subjects/search/?sub_name=xxx&code=xxx&department=xxx&faculty=xxx

- All params are optional, just pass the parameter as required for search.
- If no params are passed, all subjects will be returned.
- Faculty with semester is not available right now but will be added soon.

## Notice

Endpoint : /api/notice/search/?keyword=xxx&category=xxx&notice_type=xxx&department=xxx&is_featured=xxx&published_date=xxx&start_date=xxx&end_date=xxx

- All params are optional, just pass the parameter as required for search.
- If no params are passed, all notices will be returned.
- is_featured can be either true or false.
- published_date, start_date and end_date should be in YYYY-MM-DD format.
- start_date and end_date are used to filter notices based on published_date range.

### Authentication (JWT)

- To get the token, send a POST request to /api/token/ with username and password in the body.
- To refresh the token, send a POST request to /api/token/refresh/ with refresh token in the body.

#### To access the protected endpoints, send the token in the Authorization header as Bearer token.

# TCIOE

Search Endpoints:

- Staffs: /api/department/staffs/search/?name=xxx&designation=xxx&department=xxx&key_officials=xxx

  - All params are optional, just pass the parameter as required for search.
  - If no params are passed, all staffs will be returned.
  - key_officials can be either true or false.

- Subjects : /api/department/subjects/search/?sub_name=xxx&code=xxx&department=xxx&faculty=xxx

  - All params are optional, just pass the parameter as required for search.
  - If no params are passed, all subjects will be returned.

  - Faculty with semester is not available right now but will be added soon.

        <!-- keyword = self.request.GET.get('keyword', '')
        category = self.request.GET.get('category', '')
        notice_type = self.request.GET.get('notice_type', '')
        department = self.request.GET.get('department', '')
        is_featured = self.request.GET.get('is_featured', '')
        published_date = self.request.GET.get('published_date', '')
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '') -->

-Notice : /api/notice/search/?keyword=xxx&category=xxx&notice_type=xxx&department=xxx&is_featured=xxx&published_date=xxx&start_date=xxx&end_date=xxx

    - All params are optional, just pass the parameter as required for search.
    - If no params are passed, all notices will be returned.
    - is_featured can be either true or false.
    - published_date, start_date and end_date should be in YYYY-MM-DD format.
    - start_date and end_date are used to filter notices based on published_date range.

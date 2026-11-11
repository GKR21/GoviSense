# Dashboard Task 11 — JWT authentication and role gates

Implemented the dashboard’s real backend login flow.

- Login now sends the backend’s required `username` field and preserves the returned JWT.
- The session is created only when the response contains a valid token and supported server role.
- Officer, Admin and Farmer roles are taken from the server response and routed to their corresponding workspace.
- An unauthenticated or role-incompatible dashboard URL opens the login screen instead of bypassing authentication.
- No mobile files were changed.

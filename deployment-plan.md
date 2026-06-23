# Deployment Plan: Railway

Your Google MCP server has been modified to support seamless deployment on [Railway](https://railway.app/). 

Because committing `credentials.json` and `token.json` to GitHub is a major security risk, the application is configured to read these credentials from **Environment Variables** in production.

Follow these steps to deploy your server live:

## 1. Connect Railway to GitHub
1. Log into your [Railway](https://railway.app/) dashboard.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your repository: `yv12/MCP-Server-Gmail-GoogleDocs-`.
4. Railway will immediately attempt to build and deploy. Wait a moment; the *initial* deployment might fail because the required Google credentials are not yet injected.

## 2. Inject Google Credentials
You must provide the raw JSON contents of your local credential files so the server can authenticate with Google Docs and Gmail.

1. Click on your newly created service in the Railway dashboard.
2. Navigate to the **Variables** tab.
3. Click **New Variable**:
   - **VARIABLE_NAME**: `GOOGLE_CREDENTIALS_JSON`
   - **VALUE**: Open your local `credentials.json` file, copy all the text, and paste it here.
4. Add a second variable:
   - **VARIABLE_NAME**: `GOOGLE_TOKEN_JSON`
   - **VALUE**: Open your local `token.json` file, copy all the text, and paste it here.

## 3. Verify Deployment
1. Once you add the variables, Railway will automatically trigger a new deployment.
2. Wait for the build process to finish.
3. Navigate to the **Settings** tab in Railway.
4. Under **Networking**, click **Generate Domain** (if one wasn't generated automatically).
5. Your MCP Server is now live! 

### Connect to the Live Server
You can connect your LLM (like Claude Desktop) to the live server using the SSE endpoint:
`https://<your-railway-domain>/sse`

> **Note:** If your Google OAuth token ever expires and fails to refresh automatically, you may need to run the server locally again to generate a new `token.json`, and then update the `GOOGLE_TOKEN_JSON` variable in Railway.

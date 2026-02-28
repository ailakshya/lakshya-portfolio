# CI/CD Setup Guide

To enable automatic deployment when you push to GitHub, you need to configure two secrets in your GitHub repository.

## 1. Get Your Credentials

### **CLOUDFLARE_ACCOUNT_ID**
1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com).
2. Look at the URL in your browser address bar.
   - It will look like `https://dash.cloudflare.com/YOUR_ACCOUNT_ID/workers/...`
   - Copy that long string (e.g., `8ac6054e727fbfd99ced86c9705a5893`).
3. Alternatively, click "Workers & Pages" and find "Account ID" on the right sidebar.

### **CLOUDFLARE_API_TOKEN**
1. Go to [User Profile > API Tokens](https://dash.cloudflare.com/profile/api-tokens).
2. Click **Create Token**.
3. Use the **Edit Cloudflare Workers** template.
4. Set **Account Resources** to "Include" > "Your Account".
5. Click **Continue to summary** -> **Create Token**.
6. Copy the token immediately (you won't see it again).

## 2. Add Secrets to GitHub

1. Go to your GitHub repository.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret**.
4. Add the following two secrets:
   - Name: `CLOUDFLARE_ACCOUNT_ID`
     - Value: Check instructions above.
   - Name: `CLOUDFLARE_API_TOKEN`
     - Value: Paste your long API token.

## 3. Test It
1. Make a change to your code.
2. Commit and push/sync to the `main` branch.
3. Go to the **Actions** tab in your GitHub repo to fail/success status.

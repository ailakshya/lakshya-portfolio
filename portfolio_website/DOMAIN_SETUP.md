# Setting up Custom Domains (ailakshya.in)

To serve your portfolio at `ailakshya.in` and `www.ailakshya.in`, follow these steps in the Cloudflare Dashboard:

## 1. Navigate to Project Settings
1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Go to **Workers & Pages** and select your `lakshya-portfolio` project.
3. Click on the **Custom domains** tab.

## 2. Add the Root Domain
1. Click **Set up a custom domain**.
2. Enter `ailakshya.in` in the domain field.
3. Click **Continue**.
4. **If your domain is managed by Cloudflare DNS**:
   - Cloudflare will automatically configure the DNS records.
   - Click **Activate domain**.
5. **If your domain is managed elsewhere (e.g., GoDaddy, Namecheap)**:
   - Cloudflare will provide you with a **CNAME** record (e.g., `lakshya-portfolio.pages.dev`).
   - Log in to your domain registrar's dashboard.
   - Add a CNAME record with:
     - **Name/Host**: `@` (or `ailakshya.in`)
     - **Target/Value**: `lakshya-portfolio.pages.dev`
   - _Note: Some registrars don't allow CNAME on root (@). In that case, you might need to use Cloudflare as your nameserver._

## 3. Add the WWW Subdomain
1. Back in the **Custom domains** tab, click **Set up a custom domain** again.
2. Enter `www.ailakshya.in`.
3. Click **Continue**.
4. Follow the same DNS verification process:
   - If external, add a CNAME record:
     - **Name/Host**: `www`
     - **Target/Value**: `lakshya-portfolio.pages.dev`

## 4. Verify
- It may take a few minutes (up to 24 hours for external DNS) for the SSL certificates to issue and DNS to propagate.
- Visit `https://ailakshya.in` to check.

## 5. Automated Setup via Wrangler (Configured)

I have configured `wrangler.jsonc` to automatically handle these domains during deployment. When you run `npx wrangler deploy` (or push to GitHub), Cloudflare will attempt to routing `ailakshya.in` and `www.ailakshya.in` to this Worker.

**Prerequisite**: The domain `ailakshya.in` must be added to your Cloudflare account for this to work automatically.

## 6. Troubleshooting: Existing DNS Records

If you see an error like `Hostname 'ailakshya.in' already has externally managed DNS records`, it means you have old A or CNAME records in your Cloudflare DNS settings.

1. Go to your Cloudflare Dashboard > DNS.
2. Delete any A, AAAA, or CNAME records for `@` (root) and `www`.
3. Retry the deployment: `npx wrangler deploy`.

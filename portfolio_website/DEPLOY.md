# Deploying to Cloudflare Pages

This portfolio is ready to be hosted on Cloudflare Pages.

## Option 1: Direct Upload (Easiest)
1. Go to [Cloudflare Pages](https://pages.cloudflare.com/).
2. Click **Create a project** > **Direct upload**.
3. Upload this entire `portfolio_website` folder.
4. Click **Deploy site**.

## Option 2: Connect to GitHub (Recommended for updates)
1. Create a new repository on GitHub (e.g., `my-portfolio`).
2. Push this folder to that repository:
   ```bash
   cd portfolio_website
   git init
   git add .
   git commit -m "Initial portfolio commit"
   git remote add origin https://github.com/YOUR_USERNAME/my-portfolio.git
   git push -u origin main
   ```
3. Go to Cloudflare Pages > **Connect to Git**.
4. Select your new repository.
5. Use the following settings:
   - **Framework preset**: None (Static HTML)
   - **Build command**: (Leave empty)
   - **Output directory**: (Leave empty or use `/` if required)

## Local Testing
If you have Node.js installed, you can test locally using `wrangler` (Cloudflare CLI):
```bash
npx wrangler pages dev .
```

# Portfolio Maintenance Guide

This guide explains how to make changes to your portfolio website and deploy them.

## 1. Making Changes
All your website content is located in the `public/` folder.
- **Content & Structure**: Edit `public/index.html`.
- **Styles & Colors**: Edit `public/style.css`.
- **Interactivity/Scripts**: Edit `public/script.js`.

## 2. Previewing Changes Locally
Before deploying, you should verify your changes locally to ensure everything looks correct.
1. Open your terminal in the project folder.
2. Run the development server:
   ```bash
   npx wrangler dev
   ```
3. Open the local URL provided (usually `http://localhost:8787`) in your browser.
4. Press `x` in the terminal to stop the server when done.

## 3. Deploying to the Internet
Once you are happy with your changes, deploy them to Cloudflare.
1. Run the deploy command:
   ```bash
   npx wrangler deploy
   ```
2. Your changes will be live on `https://www.ailakshya.in` within seconds.
   (And `https://ailakshya.in` once you fix the DNS conflict and uncomment it in `wrangler.jsonc`).

## 4. Fixing the Root Domain (One-time Task)
Currently, only `www.ailakshya.in` is active. To enable `ailakshya.in`:
1. Log in to Cloudflare Dashboard > DNS.
2. Delete the old "A Record" for `ailakshya.in`.
3. Open `wrangler.jsonc` in this project.
4. Uncomment the lines for `ailakshya.in`.
5. Run `npx wrangler deploy` again.

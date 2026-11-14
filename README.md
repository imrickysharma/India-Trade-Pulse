# India Trade Pulse (GitHub Pages + Auto-Update)

Mobile-first iPhone dashboard for India's Monthly, Quarterly, and Annual Import/Export statistics.

## 1-Minute GitHub Setup
1. Create a new public repository on GitHub (e.g., `india-trade-pulse`).
2. Upload all files from this folder (`index.html`, `data/`, `scripts/`, `.github/`) to the `main` branch.
3. Go to **Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)`** and click **Save**.
4. Open your live GitHub Pages URL (`https://<your-username>.github.io/india-trade-pulse/`) in **Safari on iPhone** → tap **Share** → **Add to Home Screen**.

## Automatic Monthly Updates
- The GitHub Action in `.github/workflows/update-trade-data.yml` runs automatically on the **16th of every month** (and can also be triggered anytime under the **Actions** tab → **Run workflow**).
- When you tap **Refresh** in the dashboard on your iPhone, it fetches the updated `data/trade_data.json` plus live World Bank annual benchmarks.

# GitHub Pages Deployment Guide

This guide explains how to deploy your German Language Learner lessons to GitHub Pages.

## Architecture

The deployment consists of:
- **SQLite Database** (`language_learner.db`) - Stores all lessons locally
- **Export Script** (`export_lessons.py`) - Converts DB to JSON
- **Static Site** (`docs/`) - HTML/CSS/JS viewer hosted on GitHub Pages
- **GitHub Actions** - Automates daily lessons + deployment

## Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select:
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. Click **Save**

### 2. Configure Repository Permissions

The GitHub Actions workflow needs write permissions:

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### 3. Initial Deployment

Run the export script locally to create the initial `lessons.json`:

```bash
python export_lessons.py
```

Then commit and push:

```bash
git add docs/lessons.json
git commit -m "feat: initial lessons export"
git push
```

### 4. Trigger First Deployment

You can manually trigger the workflow:

1. Go to **Actions** tab in your repository
2. Select **Daily German Lesson** workflow
3. Click **Run workflow** → **Run workflow**

This will:
- Run `main.py` to generate today's lesson
- Export lessons to `docs/lessons.json`
- Deploy the site to GitHub Pages

### 5. Access Your Site

After deployment completes (2-3 minutes), your site will be available at:

```
https://<your-username>.github.io/<repository-name>/
```

For example: `https://debayanbhattacharya.github.io/Language-Learner/`

## Daily Automation

The workflow runs automatically every day at 07:00 UTC:
1. Generates news summary + topic discussion
2. Saves to SQLite database
3. Exports to JSON
4. Deploys updated site to GitHub Pages

## Local Development

To test the site locally:

```bash
# Export latest lessons
python export_lessons.py

# Serve the docs folder
cd docs
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## Site Features

### Card View
- Filterable by type (news/topic), topic, model, and date
- Responsive grid layout
- Preview of first 150 characters
- Click to expand

### Expanded View (Modal)
- Full markdown rendering
- Separate sections for content and vocabulary
- Metadata display (date, model, type)
- Keyboard shortcuts (ESC to close)

### Filters
- **Type**: News or Topic discussions
- **Topic**: All unique topics from your lessons
- **Model**: All LLM models used
- **Date**: Specific date picker
- **Reset**: Clear all filters

## File Structure

```
docs/
├── index.html       # Main page structure
├── styles.css       # Styling and responsive design
├── app.js           # Filtering, rendering, modal logic
└── lessons.json     # Auto-generated from SQLite DB
```

## Troubleshooting

### Site not updating after workflow runs

1. Check the Actions tab for errors
2. Verify `docs/lessons.json` was committed
3. Clear browser cache and hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)

### Markdown not rendering properly

The site uses [marked.js](https://marked.js.org/) for markdown parsing. Ensure your content uses standard markdown syntax.

### Filters not showing options

Run `export_lessons.py` to ensure `lessons.json` has data:

```bash
python export_lessons.py
```

Check that the JSON file contains lessons with the expected fields.

## Customization

### Change Color Scheme

Edit `docs/styles.css` `:root` variables:

```css
:root {
    --primary: #2563eb;        /* Main brand color */
    --primary-dark: #1e40af;   /* Darker shade */
    --background: #f8fafc;     /* Page background */
    --card-bg: #ffffff;        /* Card background */
}
```

### Modify Card Preview Length

In `docs/app.js`, change the substring length:

```javascript
const preview = stripMarkdown(lesson.content).substring(0, 150) + '...';
//                                                          ^^^
```

### Add More Filters

1. Add HTML select/input in `docs/index.html`
2. Update `applyFilters()` in `docs/app.js`
3. Optionally populate options in `populateFilters()`

## Security Notes

- The site is **read-only** - no user data is collected
- All content is static JSON served from GitHub Pages
- API keys remain in GitHub Secrets, never exposed to the frontend
- Database file is committed to the repo (ensure no sensitive data)

## Support

For issues or questions, check:
- GitHub Actions logs for deployment errors
- Browser console for JavaScript errors
- Repository Issues tab for known problems

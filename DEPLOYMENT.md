# Deployment Checklist for Streamlit Community Cloud

## ✅ Pre-Deployment Requirements

1. **Created `requirements.txt`** with all dependencies
2. **Updated `app.py`** to use `st.secrets` for API key
3. **Created `.streamlit/config.toml`** for app configuration
4. **Updated `.gitignore`** to prevent committing secrets
5. **Removed hardcoded API key** from app.py

## 🚀 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Configure for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Community Cloud
1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set:
   - Branch: `main`
   - Main file path: `app.py`
6. Click "Advanced settings"
7. Under "Secrets", add:
   ```toml
   ALPHAVANTAGE_API_KEY = "your_api_key_here"
   ```
   (Get a free key from https://www.alphavantage.co/support/#api-key)
8. Deploy!

### 3. Verify Deployment
- App should load without errors
- Check that API calls work
- Verify market status displays correctly

## ⚠️ Common Issues & Solutions

### Issue: "Module not found"
**Solution:** Check `requirements.txt` includes all dependencies

### Issue: "API key not found"
**Solution:** Verify secrets are set correctly in Streamlit Cloud

### Issue: "Rate limit exceeded"
**Solution:** The app already waits 13s between calls to prevent this

### Issue: "Import error"
**Solution:** Ensure Python version is compatible (3.8+)

## 📝 Local Testing

Before deploying, test locally:

1. Create `.streamlit/secrets.toml`:
   ```toml
   ALPHAVANTAGE_API_KEY = "your_key_here"
   ```

2. Run:
   ```bash
   streamlit run app.py
   ```

3. Verify all features work

## 🔒 Security Notes

- ✅ Never commit `.streamlit/secrets.toml` to git
- ✅ Use Streamlit Cloud secrets for production
- ✅ API key is safely stored server-side only
- ✅ All API calls go directly to Alpha Vantage

## 📊 App Features

The deployed app includes:
- Top gainers without news (≥$3, ≥50% gain, ≥$30M market cap)
- Earnings predictions based on beat history
- Real-time market status
- Alpha Vantage API integration

## 🎯 Next Steps

After successful deployment:
1. Share the public URL
2. Monitor API usage
3. Consider upgrading Alpha Vantage plan if needed
4. Collect user feedback


# 🔐 Authentication Guide for Fraud Detection App

## 📋 Overview

This guide helps you resolve authentication issues with the Databricks Fraud Detection App.

---

## 🎯 Error: "Failed to initialize Databricks client"

### **Common Error Message:**
```
Failed to initialize Databricks client: default auth: cannot configure default credentials
Config: client_id=xxx, client_secret=***
Env: DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET
```

### **What This Means:**
- Your app is trying to authenticate with Databricks but lacks proper configuration
- This typically happens during **local development** or when environment variables are incomplete

---

## ✅ **Solution 1: Deploy to Databricks Apps (Recommended)**

**Why?** Databricks Apps handles authentication automatically when deployed.

### **Steps:**

```bash
# 1. Authenticate with Databricks CLI
databricks auth login --host https://fe-vm-industry-solutions-buildathon.cloud.databricks.com

# 2. Deploy the app
cd /Users/ashraf.osman/Downloads/fraud_detection_claims/fraud_detection_claims
databricks apps deploy frauddetection-prod --source-code-path prod/files/app

# 3. Access your app
# URL: https://your-workspace.azuredatabricks.net/apps/frauddetection-prod
```

**✅ This is the BEST solution** - authentication works automatically once deployed!

---

## ✅ **Solution 2: Configure Local Development**

If you need to run locally for development:

### **Option A: Using Personal Access Token**

1. **Generate a token:**
   - Go to: Databricks Workspace → User Settings → Access Tokens
   - Click "Generate New Token"
   - Copy the token

2. **Set environment variables:**
   ```bash
   export DATABRICKS_HOST="fe-vm-industry-solutions-buildathon.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token-here"
   ```

3. **Run the app:**
   ```bash
   cd prod/files/app
   streamlit run app_databricks.py
   ```

### **Option B: Using ~/.databrickscfg**

1. **Create/edit the config file:**
   ```bash
   vi ~/.databrickscfg
   ```

2. **Add your profile:**
   ```ini
   [DEFAULT]
   host = https://fe-vm-industry-solutions-buildathon.cloud.databricks.com
   token = your-personal-access-token-here
   ```

3. **Run the app:**
   ```bash
   cd prod/files/app
   streamlit run app_databricks.py
   ```

### **Option C: Using OAuth Service Principal**

1. **Set environment variables:**
   ```bash
   export DATABRICKS_HOST="fe-vm-industry-solutions-buildathon.cloud.databricks.com"
   export DATABRICKS_CLIENT_ID="your-client-id"
   export DATABRICKS_CLIENT_SECRET="your-client-secret"
   ```

2. **Run the app:**
   ```bash
   cd prod/files/app
   streamlit run app_databricks.py
   ```

---

## 🔍 **Troubleshooting by Error Type**

### **Error: "Invalid access token"**

**Cause:** Token expired or incorrect

**Fix:**
```bash
# Regenerate token and update config
databricks auth login --host https://your-workspace.azuredatabricks.com
```

### **Error: "Host not configured"**

**Cause:** DATABRICKS_HOST not set

**Fix:**
```bash
export DATABRICKS_HOST="fe-vm-industry-solutions-buildathon.cloud.databricks.com"
```

### **Error: "Cannot configure default credentials"**

**Cause:** Running locally without auth configuration

**Fix:**
- Deploy to Databricks Apps (best option)
- Or configure local auth (see Solution 2 above)

---

## 📝 **Configuration Checklist**

### **For Databricks Apps Deployment:**
- ✅ `app.yaml` configured with environment variables
- ✅ Service principal created (automatic during deployment)
- ✅ Permissions granted via `grant_permissions.sh`
- ✅ App deployed with `databricks apps deploy`

### **For Local Development:**
- ✅ DATABRICKS_HOST set (or in ~/.databrickscfg)
- ✅ DATABRICKS_TOKEN set (or in ~/.databrickscfg)
- ✅ Valid personal access token generated
- ✅ Token has necessary permissions

---

## 🚀 **Quick Start Commands**

### **Deploy to Production (Recommended):**
```bash
# From project root
cd /Users/ashraf.osman/Downloads/fraud_detection_claims/fraud_detection_claims

# Authenticate
databricks auth login --host https://fe-vm-industry-solutions-buildathon.cloud.databricks.com

# Deploy
databricks apps deploy frauddetection-prod --source-code-path prod/files/app

# Access at: https://your-workspace.azuredatabricks.net/apps/frauddetection-prod
```

### **Run Locally (Development):**
```bash
# Set environment variables
export DATABRICKS_HOST="fe-vm-industry-solutions-buildathon.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token-here"

# Run app
cd prod/files/app
streamlit run app_databricks.py
```

---

## 🔐 **Authentication Methods Priority**

The app tries authentication in this order:

1. **OAuth Service Principal** (if DATABRICKS_CLIENT_ID + CLIENT_SECRET + HOST set)
2. **Token Auth** (if DATABRICKS_TOKEN + HOST set)
3. **Config File** (~/.databrickscfg)
4. **Default** (works automatically in Databricks Apps)

---

## 📚 **Official Documentation**

- **Databricks Authentication**: https://docs.databricks.com/en/dev-tools/auth.html
- **Databricks Apps**: https://docs.databricks.com/en/dev-tools/databricks-apps.html
- **Service Principals**: https://docs.databricks.com/en/administration-guide/users-groups/service-principals.html

---

## 💡 **Best Practices**

### **For Production:**
✅ Deploy to Databricks Apps  
✅ Use service principal authentication  
✅ Grant minimum required permissions  
✅ Monitor app logs regularly  

### **For Development:**
✅ Use personal access tokens  
✅ Store tokens securely (not in code)  
✅ Use separate dev/prod environments  
✅ Test locally before deploying  

---

## 🆘 **Still Having Issues?**

### **Check These:**

1. **Is your token valid?**
   ```bash
   databricks auth profiles
   ```

2. **Can you connect to Databricks?**
   ```bash
   databricks workspace list /
   ```

3. **Are environment variables set?**
   ```bash
   echo $DATABRICKS_HOST
   echo $DATABRICKS_TOKEN
   ```

4. **Is the warehouse running?**
   - Check SQL Warehouses in Databricks UI
   - Verify warehouse ID matches app.yaml

---

## 📞 **Support Resources**

- **App Documentation**: `README.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Databricks Support**: https://help.databricks.com

---

## ✅ **Summary**

**Problem:** Authentication errors when running the app  
**Best Solution:** Deploy to Databricks Apps (automatic auth)  
**Alternative:** Configure local auth with token or config file  
**Documentation**: https://docs.databricks.com/en/dev-tools/auth.html  

**Once deployed to Databricks Apps, authentication works automatically!** 🎉

---

**Last Updated:** December 2024  
**Applies To:** Fraud Detection App v2.0+


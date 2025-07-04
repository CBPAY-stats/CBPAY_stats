# CBPAY Token Holders Tracker

A real-time dashboard showing all CBPAY token holders on the XDB Chain, automatically updated every hour.

## 🚀 Features

- **Complete holder list**: Shows all 33,420+ CBPAY token holders
- **Real-time data**: Updates automatically every hour via GitHub Actions
- **Interactive interface**: Search, sort, and paginate through holders
- **Direct links**: Click any address to view it on the XDB Chain explorer
- **Responsive design**: Works on desktop and mobile devices
- **Live statistics**: Total holders count and percentage distribution

## 📊 Live Demo

Visit the live dashboard: [Your GitHub Pages URL will be here]

## 🛠️ Setup Instructions

### 1. Fork/Clone this Repository

```bash
git clone https://github.com/yourusername/cbpay-holders-tracker.git
cd cbpay-holders-tracker
```

### 2. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages" section
3. Select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Click "Save"

### 3. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will automatically run every hour to update the data

### 4. Manual Data Update (Optional)

To manually trigger a data update:

1. Go to the "Actions" tab
2. Click on "Update CBPAY Holders Data"
3. Click "Run workflow"

## 📁 Project Structure

```
├── index.html                    # Main dashboard page
├── get_cbpay_all_holders.py     # Data collection script
├── cbpay_holders.json           # Holders data (auto-generated)
├── .github/workflows/
│   └── update-data.yml          # GitHub Actions workflow
└── README.md                    # This file
```

## 🔄 How It Works

1. **Data Collection**: The Python script queries the XDB Chain Horizon API to get all CBPAY holders
2. **Automatic Updates**: GitHub Actions runs the script every hour and commits updated data
3. **Static Hosting**: GitHub Pages serves the HTML dashboard with the latest data
4. **Real-time Display**: The webpage loads the JSON data and displays it in an interactive table

## 🎨 Customization

### Change Update Frequency

Edit `.github/workflows/update-data.yml` and modify the cron schedule:

```yaml
schedule:
  # Every 30 minutes: '*/30 * * * *'
  # Every 2 hours: '0 */2 * * *'
  # Daily at midnight: '0 0 * * *'
  - cron: '0 * * * *'  # Current: every hour
```

### Modify the Design

Edit `index.html` to customize:
- Colors and styling (CSS section)
- Layout and components
- Table columns and data display

## 📋 Requirements

- GitHub account (for hosting and automation)
- No server or database required
- All processing happens via GitHub Actions

## 🔧 Technical Details

- **Data Source**: XDB Chain Horizon API
- **Update Method**: GitHub Actions with Python script
- **Hosting**: GitHub Pages (static hosting)
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Data Format**: JSON file updated automatically

## 📈 Data Accuracy

- Data is fetched directly from the XDB Chain blockchain
- Updates reflect real-time blockchain state
- Maximum delay: 1 hour (or your configured interval)
- Includes all wallet balance changes, new holders, and removed holders

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- [XDB Chain Explorer](https://explorer.xdbchain.com/)
- [CBPAY Token Info](https://pay.coinbar.io/cbpay/)
- [XDB Chain Documentation](https://developer.xdbchain.com/)

---

**Note**: This is an unofficial tracker. For official CBPAY information, visit [pay.coinbar.io](https://pay.coinbar.io/cbpay/).


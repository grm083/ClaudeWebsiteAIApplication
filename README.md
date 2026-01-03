# Web Automation Bot with Google Gemini AI

An intelligent web automation application that uses Google's Gemini AI to navigate websites, fill out forms, and perform data entry tasks using your personal profile information.

## Features

- **AI-Powered Form Filling**: Uses Google Gemini to intelligently understand web pages and fill forms
- **Visible Browser Automation**: See every action the bot takes in real-time
- **Profile-Based Data Entry**: Maintains your information in a simple text file
- **Interactive Control**: Prompt-based interaction with manual override options
- **Customizable Delays**: 1-second delay between actions for visibility
- **Login Support**: Handles authentication when needed
- **Safe & Controllable**: Stop at any time with Ctrl+C

## Prerequisites

1. **Python 3.8 or higher**
2. **Google Chrome browser** (latest version)
3. **Google Gemini API Key** - Get one free at [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

### Step 1: Clone or Download This Repository

```bash
cd ClaudeWebsiteAIApplication
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - Web browser automation
- `google-generativeai` - Google Gemini AI integration
- `python-dotenv` - Environment variable management
- `webdriver-manager` - Automatic ChromeDriver management
- `pyinstaller` - For creating .exe file

### Step 3: Configure Your API Key

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
   (On Linux/Mac: `cp .env.example .env`)

2. Edit the `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### Step 4: Configure Your Profile

Edit `profile.txt` with your personal information. The AI will use this data to fill out web forms.

Example:
```
First Name: John
Last Name: Doe
Email: john.doe@example.com
Phone: (555) 123-4567
...
```

## Usage

### Running from Python

```bash
python web_automation.py
```

### Creating an Executable (.exe) File

To create a standalone .exe file that you can run without Python installed:

#### On Windows:

```bash
pyinstaller --onefile --noconsole --add-data ".env;." --add-data "profile.txt;." web_automation.py
```

#### On Linux/Mac:

```bash
pyinstaller --onefile --add-data ".env:." --add-data "profile.txt:." web_automation.py
```

The executable will be created in the `dist` folder.

**Important Notes for .exe:**
- The `.env` and `profile.txt` files must be in the same directory as the .exe
- Make sure to configure these files before distributing or running the .exe
- The .exe will be quite large (50-100MB) as it includes Python and all dependencies

### Alternative: Simpler .exe Creation

For easier distribution, create the .exe without bundling data files:

```bash
pyinstaller --onefile web_automation.py
```

Then keep `.env` and `profile.txt` in the same folder as the generated .exe file.

## How It Works

1. **Initialization**
   - Loads your Gemini API key from `.env`
   - Reads your profile data from `profile.txt`
   - Opens a visible Chrome browser window

2. **Website Navigation**
   - Prompts you for the target website URL
   - Navigates to the website
   - Asks if login is required

3. **Login Handling** (if needed)
   - Prompts for username/password
   - Fills login form fields
   - Waits for your manual submission

4. **Intelligent Form Filling**
   - Analyzes the page using Gemini AI
   - Identifies form fields and their purpose
   - Matches fields with your profile data
   - Fills forms with 1-second delays between actions

5. **Continuous Operation**
   - Continues processing pages until you stop
   - Allows navigation to new pages
   - Provides manual control at each step

## Application Flow

```
Start Application
    ↓
Load API Key & Profile
    ↓
Open Browser (visible)
    ↓
Prompt: Enter Website URL
    ↓
Navigate to Website
    ↓
Prompt: Login Required? (y/n)
    ↓
[If Yes] → Enter Credentials → Fill Login Form
    ↓
AI Analyzes Page
    ↓
AI Fills Forms (with 1s delays)
    ↓
Prompt: Continue / Navigate / Stop?
    ↓
[Loop until user chooses Stop or Ctrl+C]
    ↓
Close Browser
    ↓
Exit
```

## Safety & Best Practices

- **Terms of Service**: Only use this on websites where automated interaction is permitted
- **Rate Limiting**: The 1-second delay helps avoid overwhelming servers
- **Manual Review**: Always review filled forms before submission
- **Secure Credentials**: Never share your `.env` file or commit it to version control
- **Data Privacy**: Keep `profile.txt` private and secure

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you've created the `.env` file
- Check that your API key is correctly entered
- Ensure the `.env` file is in the same directory as the script

### "Chrome/ChromeDriver not found"
- Install Google Chrome if not already installed
- The `webdriver-manager` package should auto-download ChromeDriver
- If issues persist, manually install ChromeDriver from https://chromedriver.chromium.org/

### "profile.txt not found"
- The script will create a template automatically
- Fill it out and run the script again

### Forms not filling correctly
- Check that your `profile.txt` has the required fields
- Review the AI's analysis output to see what it detected
- Some websites use non-standard form structures that may need manual intervention

### .exe file too large
- This is normal - it includes Python and all dependencies
- Typical size: 50-150MB
- For smaller size, users can install Python and run the .py file directly

## File Structure

```
ClaudeWebsiteAIApplication/
├── web_automation.py      # Main application script
├── profile.txt            # Your personal information
├── .env                   # API key (create from .env.example)
├── .env.example          # Template for .env file
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── dist/                # Generated .exe files (after PyInstaller)
    └── web_automation.exe
```

## Customization

### Adding Custom Profile Fields

Add any custom fields to `profile.txt`:
```
Custom Field: Your Value
Another Field: Another Value
```

### Adjusting Action Delay

Edit `web_automation.py` line 33:
```python
self.delay = 1  # Change to desired seconds
```

### Changing AI Model

Edit `web_automation.py` line 31 to use a different Gemini model:
```python
self.model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro' for better quality
```

## Limitations

- Requires active internet connection
- Gemini API has rate limits (free tier: 60 requests/minute)
- Some websites with heavy JavaScript or CAPTCHA may not work
- Complex multi-step workflows may require manual intervention

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Google Gemini API documentation: https://ai.google.dev/docs
3. Check Selenium documentation: https://selenium-python.readthedocs.io/

## License

This project is provided as-is for personal use. Always comply with website terms of service and applicable laws when using web automation tools.

## Version

**Version 1.0.0** - Initial release

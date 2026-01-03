"""
Web Automation Application with Google Gemini AI
Automates web form filling and navigation using AI assistance
"""

import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai
from dotenv import load_dotenv
import json

class WebAutomationBot:
    def __init__(self):
        """Initialize the web automation bot"""
        # Load environment variables
        load_dotenv()

        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please create a .env file with your API key.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Load profile data
        self.profile_data = self.load_profile()

        # Initialize browser
        self.driver = None
        self.delay = 1  # 1 second delay between actions

    def load_profile(self):
        """Load user profile data from profile.txt"""
        profile_path = 'profile.txt'
        if not os.path.exists(profile_path):
            print(f"Warning: {profile_path} not found. Creating template...")
            self.create_profile_template()
            print(f"Please fill out {profile_path} with your information and run again.")
            sys.exit(1)

        profile_data = {}
        with open(profile_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    key, value = line.split(':', 1)
                    profile_data[key.strip()] = value.strip()

        return profile_data

    def create_profile_template(self):
        """Create a template profile.txt file"""
        template = """# User Profile Data
# Fill in your information below. This data will be used by the AI to fill out web forms.
# Format: key: value

# Personal Information
First Name:
Last Name:
Full Name:
Email:
Phone:
Date of Birth:
Age:

# Address Information
Street Address:
City:
State:
Zip Code:
Country:

# Professional Information
Company:
Job Title:
Industry:
Years of Experience:

# Additional Information
LinkedIn:
Website:
Skills:
Interests:

# Add any other custom fields you need below:
"""
        with open('profile.txt', 'w', encoding='utf-8') as f:
            f.write(template)

    def setup_browser(self):
        """Setup and configure the Selenium WebDriver"""
        print("Initializing browser...")
        options = webdriver.ChromeOptions()
        # Make browser visible (not headless)
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            self.driver = webdriver.Chrome(options=options)
            print("Browser initialized successfully!")
        except Exception as e:
            print(f"Error initializing browser: {e}")
            print("Make sure Chrome and ChromeDriver are installed.")
            print("You can install ChromeDriver via: pip install webdriver-manager")
            raise

    def navigate_to_website(self, url):
        """Navigate to the specified website"""
        if not url.startswith('http'):
            url = 'https://' + url

        print(f"\nNavigating to: {url}")
        self.driver.get(url)
        time.sleep(self.delay * 2)  # Give page time to load
        print("Page loaded successfully!")

    def get_page_info(self):
        """Get information about the current page"""
        try:
            # Get page title and URL
            title = self.driver.title
            url = self.driver.current_url

            # Get all forms on the page
            forms = self.driver.find_elements(By.TAG_NAME, 'form')

            # Get all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            textareas = self.driver.find_elements(By.TAG_NAME, 'textarea')
            selects = self.driver.find_elements(By.TAG_NAME, 'select')

            # Get visible text on page (first 500 chars)
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text[:500]

            page_info = {
                'title': title,
                'url': url,
                'num_forms': len(forms),
                'num_inputs': len(inputs),
                'num_textareas': len(textareas),
                'num_selects': len(selects),
                'preview': page_text
            }

            return page_info
        except Exception as e:
            print(f"Error getting page info: {e}")
            return None

    def analyze_page_with_ai(self):
        """Use Gemini AI to analyze the current page and suggest actions"""
        page_info = self.get_page_info()

        if not page_info:
            return None

        # Get form fields info
        form_fields = []
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            for inp in inputs[:20]:  # Limit to first 20 fields
                try:
                    field_info = {
                        'tag': 'input',
                        'type': inp.get_attribute('type'),
                        'name': inp.get_attribute('name'),
                        'id': inp.get_attribute('id'),
                        'placeholder': inp.get_attribute('placeholder'),
                        'visible': inp.is_displayed()
                    }
                    form_fields.append(field_info)
                except:
                    continue
        except:
            pass

        # Create prompt for Gemini
        prompt = f"""You are helping automate web form filling. Analyze this webpage and suggest what actions to take.

Page Information:
- Title: {page_info['title']}
- URL: {page_info['url']}
- Number of forms: {page_info['num_forms']}
- Number of input fields: {page_info['num_inputs']}
- Page preview: {page_info['preview']}

Form Fields Found:
{json.dumps(form_fields, indent=2)}

User Profile Data Available:
{json.dumps(self.profile_data, indent=2)}

Based on this information, provide a response in the following JSON format:
{{
    "page_type": "description of what type of page this is (e.g., login, registration, contact form, etc.)",
    "suggested_action": "what the bot should do next (e.g., fill_login, fill_registration, fill_contact_form, click_button, wait, done)",
    "requires_credentials": true/false,
    "explanation": "brief explanation of what you see and why you suggest this action"
}}

Only respond with the JSON object, no other text."""

        try:
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()

            # Try to extract JSON from the response
            if '```json' in ai_response:
                ai_response = ai_response.split('```json')[1].split('```')[0].strip()
            elif '```' in ai_response:
                ai_response = ai_response.split('```')[1].split('```')[0].strip()

            analysis = json.loads(ai_response)
            return analysis
        except Exception as e:
            print(f"Error analyzing page with AI: {e}")
            return None

    def fill_form_field(self, field, value):
        """Fill a form field with the given value"""
        try:
            if field.is_displayed() and field.is_enabled():
                field.clear()
                time.sleep(self.delay / 2)
                field.send_keys(value)
                time.sleep(self.delay)
                return True
        except Exception as e:
            print(f"Error filling field: {e}")
        return False

    def smart_fill_forms(self):
        """Use AI to intelligently fill forms on the page"""
        print("\nAnalyzing page with AI...")
        analysis = self.analyze_page_with_ai()

        if not analysis:
            print("Could not analyze page. Skipping...")
            return False

        print(f"\nAI Analysis:")
        print(f"  Page Type: {analysis.get('page_type', 'Unknown')}")
        print(f"  Suggested Action: {analysis.get('suggested_action', 'Unknown')}")
        print(f"  Explanation: {analysis.get('explanation', 'N/A')}")

        # Get all visible input fields
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')

            filled_count = 0
            for inp in inputs:
                try:
                    if not inp.is_displayed() or not inp.is_enabled():
                        continue

                    field_type = inp.get_attribute('type')
                    field_name = inp.get_attribute('name') or ''
                    field_id = inp.get_attribute('id') or ''
                    field_placeholder = inp.get_attribute('placeholder') or ''

                    # Skip certain input types
                    if field_type in ['hidden', 'submit', 'button', 'image', 'reset']:
                        continue

                    # Use AI to determine what value to fill
                    value = self.get_field_value_from_ai(field_name, field_id, field_placeholder, field_type)

                    if value:
                        print(f"  Filling field: {field_name or field_id or field_placeholder} = {value}")
                        if self.fill_form_field(inp, value):
                            filled_count += 1

                except Exception as e:
                    continue

            print(f"\nFilled {filled_count} fields")
            return filled_count > 0

        except Exception as e:
            print(f"Error in smart_fill_forms: {e}")
            return False

    def get_field_value_from_ai(self, field_name, field_id, field_placeholder, field_type):
        """Use AI to determine what value should go in a field"""
        # Create a simple mapping prompt
        field_descriptor = field_name or field_id or field_placeholder or 'unknown'

        # Common field patterns
        field_lower = field_descriptor.lower()

        # Email fields
        if any(x in field_lower for x in ['email', 'e-mail']):
            return self.profile_data.get('Email', '')

        # Name fields
        if 'first' in field_lower and 'name' in field_lower:
            return self.profile_data.get('First Name', '')
        if 'last' in field_lower and 'name' in field_lower:
            return self.profile_data.get('Last Name', '')
        if 'full' in field_lower and 'name' in field_lower:
            return self.profile_data.get('Full Name', '')
        if field_lower in ['name', 'username', 'user_name']:
            return self.profile_data.get('Full Name', '')

        # Phone fields
        if any(x in field_lower for x in ['phone', 'tel', 'mobile', 'cell']):
            return self.profile_data.get('Phone', '')

        # Address fields
        if any(x in field_lower for x in ['address', 'street']):
            return self.profile_data.get('Street Address', '')
        if 'city' in field_lower:
            return self.profile_data.get('City', '')
        if any(x in field_lower for x in ['state', 'province']):
            return self.profile_data.get('State', '')
        if any(x in field_lower for x in ['zip', 'postal']):
            return self.profile_data.get('Zip Code', '')
        if 'country' in field_lower:
            return self.profile_data.get('Country', '')

        # Company/Job fields
        if 'company' in field_lower:
            return self.profile_data.get('Company', '')
        if any(x in field_lower for x in ['job', 'title', 'position']):
            return self.profile_data.get('Job Title', '')

        return None

    def handle_login(self, username, password):
        """Handle login form filling"""
        print("\nAttempting to fill login form...")

        try:
            # Find username field
            username_field = None
            for selector in ['input[type="email"]', 'input[type="text"]', 'input[name*="user"]', 'input[name*="email"]', 'input[id*="user"]', 'input[id*="email"]']:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if username_field.is_displayed():
                        break
                except:
                    continue

            if username_field:
                print(f"  Found username field")
                self.fill_form_field(username_field, username)

            # Find password field
            password_field = None
            try:
                password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            except:
                pass

            if password_field and password_field.is_displayed():
                print(f"  Found password field")
                self.fill_form_field(password_field, password)

            print("\nLogin fields filled. Please review and submit manually, or press Enter to continue...")
            input()

        except Exception as e:
            print(f"Error handling login: {e}")

    def run(self):
        """Main execution loop"""
        print("=" * 60)
        print("  Web Automation Bot with Google Gemini AI")
        print("=" * 60)
        print("\nThis bot will help you automate web form filling.")
        print("Actions will be visible in the browser window.")
        print("Press Ctrl+C at any time to stop.\n")

        try:
            # Setup browser
            self.setup_browser()

            # Get target website
            url = input("Enter the website URL you want to interact with: ").strip()
            if not url:
                print("No URL provided. Exiting...")
                return

            # Navigate to website
            self.navigate_to_website(url)

            # Check if login is needed
            needs_login = input("\nDoes this site require login? (y/n): ").strip().lower()

            if needs_login == 'y':
                username = input("Enter username/email: ").strip()
                password = input("Enter password: ").strip()
                self.handle_login(username, password)
                time.sleep(self.delay * 2)

            # Main automation loop
            print("\n" + "=" * 60)
            print("Starting automation...")
            print("Press Ctrl+C to stop at any time")
            print("=" * 60)

            action_count = 0
            while True:
                action_count += 1
                print(f"\n--- Action #{action_count} ---")

                # Try to fill forms
                if self.smart_fill_forms():
                    print("\nForms filled! Review the entries in the browser.")
                else:
                    print("\nNo forms to fill on this page.")

                # Ask user what to do next
                print("\nOptions:")
                print("  1. Continue to next action")
                print("  2. Navigate to different page on same site")
                print("  3. Stop automation")

                choice = input("\nEnter choice (1-3) or press Enter to continue: ").strip()

                if choice == '3':
                    print("\nStopping automation...")
                    break
                elif choice == '2':
                    new_url = input("Enter new URL (or relative path): ").strip()
                    if new_url:
                        if not new_url.startswith('http'):
                            # Relative URL
                            current_url = self.driver.current_url
                            base_url = '/'.join(current_url.split('/')[:3])
                            new_url = base_url + '/' + new_url.lstrip('/')
                        self.navigate_to_website(new_url)
                else:
                    # Continue
                    time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\n\nAutomation stopped by user (Ctrl+C)")
        except Exception as e:
            print(f"\nError during execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            if self.driver:
                print("\nClosing browser in 3 seconds...")
                time.sleep(3)
                self.driver.quit()
            print("Automation complete. Goodbye!")

def main():
    """Main entry point"""
    try:
        bot = WebAutomationBot()
        bot.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()

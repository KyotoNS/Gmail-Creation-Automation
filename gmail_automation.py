import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from unidecode import unidecode

# CONFIG
api_key = ""  # ← Replace this with your real API key

# Chrome setup with improved fingerprinting
chrome_options = ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

# WebDriver service
service = ChromeService('chromedriver.exe')
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)  # Set a realistic window size

# Name pools
first_names = ["Chase","Zachary","Darcy","Jackson","Adam","Sebastian","Noah","Leo","Nathaniel","Riley"]
last_names = ["Hamiltom","Edwards","Wenham","Harrison","Allen","Robinson","Carter","Morgan","Johnston","Tran"]

first_name = random.choice(first_names)
last_name = random.choice(last_names)
first_name_norm = unidecode(first_name).lower()
last_name_norm = unidecode(last_name).lower()
username = f"{first_name_norm}{last_name_norm}{random.randint(1000, 9999)}"
password = "M@r@h7563845;"
birthday = ("05", "3", "1989")
gender = "1"  # Female

# SMS-Activate API functions
def get_sms_number():
    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={api_key}&action=getNumber&service=go&country=6"
    response = requests.get(url).text
    if not response.startswith("ACCESS"):
        raise Exception("Failed to get number:", response)
    parts = response.split(":")
    return {"id": parts[1], "number": parts[2]}

def set_status(id, status):
    requests.get(f"https://api.sms-activate.org/stubs/handler_api.php?api_key={api_key}&action=setStatus&status={status}&id={id}")

def get_code(id):
    for _ in range(60):  # wait up to 60s
        time.sleep(5)
        r = requests.get(f"https://api.sms-activate.org/stubs/handler_api.php?api_key={api_key}&action=getStatus&id={id}")
        if r.text.startswith("STATUS_OK"):
            return r.text.split(":")[1]
    raise TimeoutError("SMS code not received")

# --- Main Automation Flow ---
def create_account():
    global driver
    try:
        wait = WebDriverWait(driver, 60)  # Increased wait time
        driver.get("https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Ensure page loads
        
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(random.randint(1, 10))

        # Fill name
        print("Filling name...")
        time.sleep(random.randint(1, 10))
        wait.until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(first_name)
        time.sleep(random.randint(1, 10))
        driver.find_element(By.NAME, "lastName").send_keys(last_name)
        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe"))).click()

        # Birthday & gender
        print("Filling birthday and gender...")
        time.sleep(random.randint(1, 10))
        wait.until(EC.visibility_of_element_located((By.ID, "day")))
        time.sleep(random.randint(1, 10))
        Select(driver.find_element(By.ID, "month")).select_by_value(birthday[1])
        time.sleep(random.randint(1, 10))
        driver.find_element(By.ID, "day").send_keys(birthday[0])
        time.sleep(random.randint(1, 10))
        driver.find_element(By.ID, "year").send_keys(birthday[2])
        time.sleep(random.randint(1, 10))
        Select(driver.find_element(By.ID, "gender")).select_by_value(gender)
        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe"))).click()

        # Check which username page appears
        print("Checking which username page appears...")
        suggestion_page_detected = False
        direct_username_page_detected = False

        # Check for "Choose your Gmail address" page (first screenshot)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pilih alamat Gmail Anda') or contains(text(), 'Choose your Gmail address')]")))
            print("Scenario 1: 'Choose your Gmail address' page detected.")
            suggestion_page_detected = True
        except:
            # Check for "How you’ll sign in" page (second screenshot)
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'How you’ll sign in') or contains(text(), 'Cara Anda akan masuk')]")))
                print("Scenario 2: 'How you’ll sign in' page detected.")
                direct_username_page_detected = True
            except:
                # If neither page is detected, check if we’ve moved to the password step
                try:
                    wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
                    print("Scenario 3: Username accepted directly, proceeding to password step...")
                except:
                    raise Exception("Neither username page nor password field found. Page flow may have changed.")

        # Handle "Choose your Gmail address" page (first screenshot)
        if suggestion_page_detected:
            print("Selecting 'Create your own' option...")
            custom_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Buat alamat Gmail Anda sendiri') or contains(text(), 'Create your own Gmail address')]")))
            custom_option.click()
            try:
                username_input = wait.until(EC.visibility_of_element_located((By.NAME, "Username")))
                username_input.clear()
                time.sleep(random.randint(1, 10))
                username_input.send_keys(username)
                print(f"Reusing existing username: {username}@gmail.com")
                time.sleep(10)
                next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe")))
                next_button.click()
                wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
                print(f"Username {username}@gmail.com accepted.")
            except:
                raise Exception(f"Username {username}@gmail.com is not available. Please choose a different username and try again.")

        # Handle "How you’ll sign in" page (second screenshot)
        elif direct_username_page_detected:
            print("Filling username directly...")
            print(f"Using username: {username}")
            if not username:
                raise ValueError("Username is not defined before use.")
            time.sleep(random.randint(1, 10))
            wait.until(EC.visibility_of_element_located((By.NAME, "Username"))).send_keys(username)
            time.sleep(10)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe"))).click()
            try:
                wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
                print(f"Username {username}@gmail.com accepted.")
            except:
                raise Exception("Failed to proceed to password step after filling username.")

# Password
        print("Filling password...")
        try:
            time.sleep(random.randint(1, 10))
            password_field = wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
            password_field.send_keys(password)
            print("Password field filled.")
            time.sleep(random.randint(1, 10))
            confirm_password_field = wait.until(EC.visibility_of_element_located((By.NAME, "PasswdAgain")))
            confirm_password_field.send_keys(password)
            print("Confirm password field filled.")
            time.sleep(10)
            next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe")))
            next_button.click()
            print("Clicked Next after password step.")
        except Exception as e:
            raise Exception(f"Failed to fill password and confirm password: {e}")

        # Validate password step
        print("Validating password step completion...")
        try:
            wait.until(EC.presence_of_element_located((By.ID, "phoneNumberId") | (By.XPATH, "//button[contains(text(), 'Skip')]") | (By.XPATH, "//*[contains(text(), 'Not now')]")))
            print("Password step completed successfully.")
        except:
            print("Warning: Could not confirm password step completion, proceeding anyway...")

        # Phone verification (required)
        print("Checking phone number step...")
        try:
            phone_field = wait.until(EC.element_to_be_clickable((By.ID, "phoneNumberId")))
            print("Phone number field found, requesting number...")
            sms_info = get_sms_number()
            print("Got number:", sms_info["number"])
            time.sleep(10)

            # Select country code (hardcoded to Indonesia)
            try:
                time.sleep(10)
                wait.until(EC.element_to_be_clickable((By.ID, "countryList")))
                time.sleep(10)
                Select(driver.find_element(By.ID, "countryList")).select_by_value("ID")
                time.sleep(10)
            except:
                print("Country code selection not found, proceeding...")

            # Strip the country code (+62) from the phone number
            phone_number = sms_info["number"]
            if phone_number.startswith("62"):
                phone_number = phone_number[2:]  # Remove "62" (2 characters)
            else:
                raise Exception(f"Unexpected phone number format: {phone_number}. Expected a number starting with +62.")
            print(f"Using phone number (without country code): {phone_number}")

            # Fill phone number with retry mechanism
            for _ in range(3):
                try:
                    time.sleep(20)
                    phone_field = wait.until(EC.element_to_be_clickable((By.ID, "phoneNumberId")))
                    phone_field.clear()  # Clear any existing text
                    phone_field.send_keys(phone_number)
                    break
                except:
                    print("Retrying phone number input...")
                    time.sleep(2)
            time.sleep(10)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe"))).click()

            # Wait for code field
            print("Waiting for code field...")
            wait.until(EC.presence_of_element_located((By.NAME, "code")))

            # Poll for SMS code
            print("Waiting for SMS...")
            code = get_code(sms_info["id"])
            print("Got code:", code)
            time.sleep(10)

            # Fill verification code
            print("Filling verification code...")
            time.sleep(10)
            driver.find_element(By.NAME, "code").send_keys(code)
            time.sleep(10)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe"))).click()
            set_status(sms_info["id"], 6)  # complete
            print("Phone verification completed.")
        except Exception as e:
            raise Exception(f"Phone verification failed: {e}. Phone verification is required to ensure account creation.")

        # Skip recovery email (optional)
        print("Checking recovery email step...")
        time.sleep(10)
        try:
            # Check if recovery email field is present
            wait.until(EC.presence_of_element_located((By.ID, "recoveryEmailId")))  # Adjust ID based on actual field
            print("Recovery email field found, attempting to skip...")
            time.sleep(10)
            try:
                # Look for Skip or Next button
                skip_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Skip')]")))
                skip_button.click()
                print("Skipped recovery email.")
            except:
                next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe")))
                next_button.click()
                print("Clicked Next to skip recovery email.")
        except:
            print("Recovery email field not found, proceeding...")

        # Handle "Review your account info" page (optional)
        print("Checking for 'Review your account info' page...")
        time.sleep(10)
        try:
            # Look for the "Next" button (text: "Next" in English, "Selanjutnya" in Indonesian)
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Selanjutnya')]")))
            next_button.click()
            time.sleep(10)
            print("Clicked 'Next' on Review your account info page.")
        except:
            try:
                # Fallback: Use the class name if the text-based locator fails
                next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe")))
                next_button.click()
                time.sleep(10)
                print("Clicked 'Next' on Review your account info page (using class name).")
            except:
                print("Review your account info page not found, proceeding to terms...")

        # Accept terms
        print("Accepting terms...")
        time.sleep(30)
        try:
            # Scroll to the bottom of the terms
            terms_container = driver.find_element(By.XPATH, "//div[contains(@class, 'bKxuT') or contains(@class, 'scrollable')]")
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", terms_container)
            print("Scrolled to the bottom of the terms.")
            time.sleep(10)  # Increased delay to ensure scroll completes

            # Check for overlays or CAPTCHAs
            try:
                captcha = driver.find_element(By.XPATH, "//*[contains(@class, 'g-recaptcha')]")
                print("CAPTCHA detected. Manual intervention required.")
                input("Please solve the CAPTCHA and press Enter to continue...")
            except:
                print("No CAPTCHA detected.")

            # Retry clicking the "I agree" button
            for attempt in range(3):
                try:
                    # Try to find the "I agree" button (support both English and Indonesian)
                    agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.//span, 'I agree') or contains(.//span, 'Saya setuju')]")))
                    actions.move_to_element(agree_button).click().perform()
                    print("Clicked 'I agree' button.")
                    break  # Exit loop if successful
                except Exception as e:
                    print(f"Attempt {attempt + 1}: Failed to click 'I agree' button: {e}")
                    if attempt == 2:  # Last attempt
                        try:
                            # Fallback: Use class name
                            agree_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "VfPpkd-LgbsSe")))
                            actions.move_to_element(agree_button).click().perform()
                            print("Clicked 'I agree' button (using class name).")
                        except Exception as e:
                            raise Exception(f"Failed to click 'I agree' button after retries: {e}")
                    time.sleep(random.uniform(2, 5))  # Wait before retrying
        except Exception as e:
            raise Exception(f"Failed to accept terms: {e}")
            
            
        # Validate that we moved past the terms step
        print("Validating terms acceptance...")
        time.sleep(10)
        try:
            # Check for an element that indicates we've moved forward (e.g., a welcome page or inbox)
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Selamat datang')]")))
            print("Terms accepted successfully.")
        except:
            print("Warning: Could not confirm terms acceptance, but proceeding...")

        # Log in to validate the account
        print("Logging in to validate account creation...")
        driver.get("https://accounts.google.com/signin")
        wait.until(EC.presence_of_element_located((By.ID, "identifierId"))).send_keys(f"{username}@gmail.com")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next') or contains(text(), 'Selanjutnya')]"))).click()
        time.sleep(1)

        # Check for "Email not found" error
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Couldn’t find your Google Account') or contains(text(), 'Tidak dapat menemukan Akun Google Anda')]")))
            raise Exception(f"Account {username}@gmail.com not found during login. Signup may have failed.")
        except:
            print("No 'Email not found' error detected, proceeding to password...")

        # Enter password
        wait.until(EC.presence_of_element_located((By.NAME, "Passwd"))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next') or contains(text(), 'Selanjutnya')]"))).click()
        time.sleep(2)

        # Validate successful login
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Selamat datang')]")))
            print(f"Successfully logged in to {username}@gmail.com")
        except:
            raise Exception(f"Failed to log in to {username}@gmail.com. Account may not have been created properly.")

        print(f"\n✅ Gmail created and verified:\nEmail: {username}@gmail.com\nPassword: {password}\n")

    except Exception as e:
        print("❌ Failed:", e)
        if 'sms_info' in locals():
            try:
                set_status(sms_info["id"], 8)  # cancel number
            except:
                pass
    finally:
        input("Press Enter to quit browser...")
        driver.quit()

create_account()
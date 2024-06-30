import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
import io
from urllib.parse import urlparse, urlunparse

def format_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'https://' + url
        parsed = urlparse(url)
    return urlunparse(parsed)

def capture_full_page(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_width = driver.execute_script("return document.documentElement.clientWidth")
    viewport_height = driver.execute_script("return document.documentElement.clientHeight")
    num_screenshots = total_height // viewport_height + 1
    full_image = Image.new('RGB', (viewport_width, total_height))
    
    for i in range(num_screenshots):
        driver.execute_script(f"window.scrollTo(0, {i * viewport_height})")
        time.sleep(0.5)
        screenshot = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        full_image.paste(image, (0, i * viewport_height))
    
    return full_image

def perform_ocr(image):
    text = pytesseract.image_to_string(image)
    return text

def auto_mode(url):
    url = format_url(url)
    print(f"Navigating to: {url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        print("Capturing full page screenshot...")
        image = capture_full_page(driver)
        return image
    finally:
        driver.quit()

def manual_mode():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("about:blank")
        print("Empty browser opened. Navigate to the desired page and press Enter when ready to capture.")
        input()
        print("Capturing full page screenshot...")
        image = capture_full_page(driver)
        return image
    finally:
        driver.quit()

# Main execution
print("Choose an option:")
print("1. Enter a URL for automatic processing")
print("2. Open an empty browser for manual navigation")

choice = input("Enter your choice (1 or 2): ")

if choice == "1":
    url = input("Enter the website URL: ")
    image = auto_mode(url)
elif choice == "2":
    image = manual_mode()
else:
    print("Invalid choice. Exiting.")
    exit()

print("Performing OCR...")
text = perform_ocr(image)

print("\nExtracted text:")
print(text)

image.save("full_page_screenshot.png")
print("\nScreenshot saved as 'full_page_screenshot.png'")
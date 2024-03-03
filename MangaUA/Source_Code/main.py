from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from time import sleep
from requests import get
from reportlab.pdfgen import canvas
from PIL import Image as PilImage


url = 'https://honey-manga.com.ua'

def download_images(name_manga, select_page, end_page):
    # Create a PDF file
    pdf_file = f'{name_manga}.pdf'
    c = canvas.Canvas(pdf_file, pagesize=letter)
    # Initialize the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Activate headless mode
    driver = webdriver.Chrome(options=options)

    # Navigate to the webpage
    driver.get(url)
    Button = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div/div[2]/button"))
    )
    Button[0].click()
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )
    search[0].send_keys(name_manga)
    Button = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "body > div.MuiDialog-root.MuiModal-root.css-4cv13i > div.MuiDialog-container.MuiDialog-scrollPaper.css-ekeie0 > div > div > div.mt-6.MuiBox-root.css-10d4j3m > button"))
    )
    Button[0].click()
    Button = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/div/div[2]/div/div/div[1]/div[2]/div[2]/div[2]/a'))
    )
    Button[0].click()
    if select_page != '':
        while True:
            sleep(0.5)
            Page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div/div/div/div[2]/div/button[2]'))
            )
            Page = Page[0].text
            print(Page)
            if len(Page.split("-")) > 1 and Page.split("-", 1)[1].strip() == select_page:
                print("Go")
                break
            else:
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/button[3]'))
                    )
                    button.click()
                except Exception:
                    # If the "Next" button is not found, exit the loop
                    break
    while True:
        # Get all images on the page
        sleep(0.5)
        images = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )

        # Download and add images to the PDF
        for img in images:
            img_url = img.get_attribute('src')
            if img_url:
                try:
                    response = get(img_url)
                    img_data = BytesIO(response.content)
                    pil_image = PilImage.open(img_data)
                    img_width, img_height = pil_image.size
                    pdf_width, pdf_height = img_width, img_height  # Set PDF page size based on image size
                    c.setPageSize((pdf_width, pdf_height))  # Set the PDF page size
                    c.drawImage(ImageReader(img_data), 0, 0, pdf_width, pdf_height)  # Add image to PDF
                    c.showPage()  # Add a new page to the PDF
                except Exception as e:
                    print(f"Error adding image to PDF: {e}")
        try:
            Page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div/div/div/div[2]/div/button[2]'))
            )
            Page = Page[0].text
            print(Page)
            if len(Page.split("-")) > 1:
                Page = Page.split("-", 1)[1].strip()
                print(Page)
                if Page == end_page:
                    print("Session ended page")
                    break
            sleep(0.5)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/button[3]'))
            )
            button.click()
        except Exception:
            # If the "Next" button is not found, exit the loop
            print("Session ended button")
            break
    c.save()
    # Quit the webdriver
    driver.quit()

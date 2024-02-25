from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import os
import shutil

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    global cur_dir
    cur_dir = os.getcwd()
    orders = get_orders()
    open_robot_order_website()
    for row in orders:
        global order_number
        global head
        global body
        global legs
        global address
        order_number = row['Order number']
        head = row['Head']
        body = row['Body']
        legs = row['Legs']
        address = row['Address']
        close_annoying_modal()
        fill_the_form()
        store_receipt_as_pdf(order_number)
        screenshot_robot(order_number)
        embed_screenshot_to_receipt(f"output/image/{order_number}.png", f"output/pdf/{order_number}.pdf")
        page.click("//*[@id='order-another']")
    archive_receipts()
        
def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    table = tables.read_table_from_csv(f'{cur_dir}/orders.csv')
    return table
    
def open_robot_order_website():
    browser.configure(
        slowmo = 100,
        headless = False
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    global page
    page = browser.page()

def close_annoying_modal():
    page.click("//*[@class='btn btn-dark']")
    
def fill_the_form():
    page.select_option("//*[@id='head']",value=f'{head}')
    page.click(f"//*[@class='form-check-input' and @value='{body}']")
    page.fill("//*[@placeholder='Enter the part number for the legs']",f'{legs}')
    page.fill("//*[@placeholder='Shipping address']",f"{address}")
    page.click("//*[@id='preview']")
    # page.screenshot("//*[@id='robot-preview-image']")
    page.click("//*[@id='order']")
    try:
        page.query_selector("//*[@id='receipt']").inner_html()
    except:
        page.click("//*[text()='Home']")
        page.click("//*[text()='Order your robot!']")
        close_annoying_modal()
        fill_the_form()

def store_receipt_as_pdf(order_number):
    receipt = page.query_selector("//*[@id='receipt']").inner_html()
    global pdf
    pdf = PDF()
    pdf.html_to_pdf(receipt,f"output/pdf/{order_number}.pdf")
    
def screenshot_robot(order_number):
    robot_img_locator = page.locator("//*[@id='robot-preview-image']")
    robot_img_locator.screenshot(path=f"output/image/{order_number}.png")
    
def embed_screenshot_to_receipt(screenshot, pdf_file):
    image = [f'{screenshot}:align=center']
    pdf.add_files_to_pdf(image, pdf_file, append=True)
    
def archive_receipts():
    archive_dir = "output/pdf.zip"
    source_dir = "output/pdf"
    shutil.make_archive(archive_dir, 'zip', source_dir)
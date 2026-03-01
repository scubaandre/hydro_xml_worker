import asyncio
import json
import logging
import os
from datetime import datetime, timedelta

import requests
from pyppeteer import connect

# --- CONFIG ---
VERSION = "0.1.9"
OPTIONS_PATH = "/data/options.json"
DOWNLOAD_DIR = "/share/hydro_ottawa"

# --- LOGGER SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s - [v{VERSION}] - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def download_hydro_data():
    # Reload config inside the function for live updates
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH, "r") as f:
            conf = json.load(f)
        user_email = conf.get("user_email")
        user_pass = conf.get("user_pass")
        browser_url = conf.get("browser_url", "ws://homeassistant:3000")
        login_timeout = conf.get("login_timeout", 30)
        debug_mode = conf.get("debug_mode", False)
        days_to_export = conf.get("days_to_export", 2)
    else:
        logger.error("Config file not found. Exiting scrape.")
        return

    # --- DYNAMIC LOG LEVEL ---
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled: Detailed logs will be shown.")
    else:
        logger.setLevel(logging.INFO)

    # --- SCREENSHOT SYSTEM ---
    screenshot_counter = 0

    def next_screenshot_name():
        nonlocal screenshot_counter
        screenshot_counter += 1
        return os.path.join(DOWNLOAD_DIR, f"debug_{screenshot_counter:02d}.png")

    async def debug_screenshot(page, label=""):
        if not debug_mode:
            return
        try:
            name = next_screenshot_name()
            logger.debug(f"Capturing screenshot: {label} → {name}")
            await page.screenshot({"path": name})
        except Exception as e:
            logger.debug(f"Failed to capture screenshot: {e}")

    browser = None
    page = None
    try:
        # 0. Calculate our target date for export based on config
        target_date_obj = datetime.now() - timedelta(days=days_to_export)
        from_date_str = target_date_obj.strftime("%Y-%m-%d")

        logger.info(
            f"Starting Scrape Process (Fetching history back to {from_date_str})"
        )

        # 1. Connect to Browserless
        logger.debug(f"Connecting to Browserless app at {browser_url}")
        browser = await connect(browserWSEndpoint=browser_url)

        page = await browser.newPage()
        await page.setViewport({"width": 1280, "height": 800})

        cdp = await page.target.createCDPSession()
        await cdp.send(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": DOWNLOAD_DIR},
        )

        # 2. Navigate to Login Page
        logger.debug(f"Opening portal for {user_email}...")
        await page.goto(
            "https://hydroottawa.savagedata.com/Connect/Authorize?returnUrl=https%3A%2F%2Fhydroottawa.savagedata.com%2F",
            {"waitUntil": "networkidle2"},
        )
        await debug_screenshot(page, "login_page_loaded")

        logger.debug(f"Waiting for page to show up")
        await page.waitForSelector("#userName", {"timeout": login_timeout * 1000})
        await debug_screenshot(page, "login_form_visible")

        # 3. Enter Credentials and Login
        logger.debug("Entering credentials...")
        await page.evaluate(
            f"""() => {{
            const e = document.querySelector('#userName');
            const p = document.querySelector('#exampleInputPassword');
            const btn = document.querySelector('a.btn-primary');
            if (e && p && btn) {{
                e.value = '{user_email}';
                p.value = '{user_pass}';
                ['input', 'change', 'blur'].forEach(v => e.dispatchEvent(new Event(v, {{bubbles:true}})));
                ['input', 'change', 'blur'].forEach(v => p.dispatchEvent(new Event(v, {{bubbles:true}})));
                btn.click();
            }}
        }}"""
        )
        await debug_screenshot(page, "credentials_entered")

        await asyncio.sleep(10)
        await debug_screenshot(page, "post_login_wait")

        # 4. Navigate to Download page
        logger.debug("Looking for DownloadMyData link...")
        nav_success = await page.evaluate(
            """() => {{
            const link = document.querySelector('a[href="DownloadMyData"]');
            if (link) {{ link.click(); return true; }}
            return false;
        }}"""
        )

        if not nav_success:
            await debug_screenshot(page, "download_link_missing")
            raise Exception(f"Navigation failed. URL: {page.url}")

        await asyncio.sleep(10)
        await debug_screenshot(page, "download_page_loaded")

        # 5. Intercept API call to fetch XML data
        download_status = {"success": False}

        async def intercept_request(request):
            if "api/Data/GetUsageData" in request.url:
                auth = request.headers.get("authorization")
                if auth:
                    logger.debug("Intercepted API call. Fetching XML...")
                    try:
                        resp = requests.get(
                            request.url, headers={"Authorization": auth}
                        )
                        if resp.status_code == 200:
                            path = os.path.join(DOWNLOAD_DIR, "hydro_data.xml")
                            with open(path, "wb") as f:
                                f.write(resp.content)
                            download_status["success"] = True
                            logger.info(f"SUCCESS: File saved to {path}")
                    except Exception as e:
                        logger.error(f"Interception failed: {e}")

        await page.setRequestInterception(True)

        async def handle_request(req):
            await intercept_request(req)
            await req.continue_()

        page.on("request", lambda req: asyncio.ensure_future(handle_request(req)))

        # 6. Click the necessary checkboxes, set the date, and export
        logger.debug(f"Setting Start Date to {from_date_str} and triggering export...")

        await page.evaluate(
            f"""async () => {{
            const dateInput = document.querySelector('.rz-datepicker input');
            if (dateInput) {{
                dateInput.focus();
                dateInput.value = '{from_date_str}';
                dateInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                dateInput.blur();
            }}

            const clickRadzenCheck = (inputId) => {{
                const input = document.getElementById(inputId);
                if (input) {{
                    const container = input.closest('.rz-chkbox');
                    const box = container ? container.querySelector('.rz-chkbox-box') : null;
                    if (box && !box.classList.contains('rz-state-active')) {{
                        box.click();
                    }}
                }}
            }};
            
            clickRadzenCheck('chkElectUsageData');
            clickRadzenCheck('chkBillingData');

            await new Promise(r => {{
                const i = setInterval(() => {{
                    if (!document.querySelector('.rz-progressbar')) {{ 
                        clearInterval(i); 
                        r(); 
                    }}
                }}, 500);
            }});

            const btn = Array.from(document.querySelectorAll('button'))
                             .find(b => b.querySelector('img[src*="gb_logo.png"]'));
            if (btn) btn.click();
        }}"""
        )

        await debug_screenshot(page, "export_triggered")

        for i in range(25):
            if download_status["success"]:
                break
            if i % 5 == 0:
                logger.debug(f"Waiting for download ({i}/25)...")
            await asyncio.sleep(1)

        if not download_status["success"]:
            await debug_screenshot(page, "download_timeout")
            logger.warning("Download did not complete within expected time window.")

    except Exception as e:
        logger.error(f"WORKER FAILED: {e}")
        if debug_mode and page is not None:
            await debug_screenshot(page, "exception")
    finally:
        if browser is not None:
            logger.debug("Closing browser.")
            await browser.close()


async def main_loop():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    logger.info(f"Hydro Ottawa Service v{VERSION} Ready.")

    while True:
        try:
            if os.path.exists(OPTIONS_PATH):
                with open(OPTIONS_PATH, "r") as f:
                    conf = json.load(f)
                scrapes_per_day = conf.get("scrapes_per_day", 4)
            else:
                scrapes_per_day = 4

            # --- GLOBAL TIMEOUT WRAPPER ---
            try:
                await asyncio.wait_for(download_hydro_data(), timeout=300)
            except asyncio.TimeoutError:
                logger.error("Scrape timed out after 300 seconds; will retry next interval.")

            sleep_seconds = 86400 / scrapes_per_day
            logger.info(f"Next scrape in {sleep_seconds/3600:.1f} hours.")
            await asyncio.sleep(sleep_seconds)

        except Exception as e:
            logger.error(f"CRITICAL: Main Loop Crash: {e}")
            await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main_loop())

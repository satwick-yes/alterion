import os
import time
from playwright.sync_api import sync_playwright

def post_to_instagram(file_path: str, caption: str) -> str:
    """
    Automates posting to Instagram using Playwright.
    Returns a status string to be spoken by Vani.
    """
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."

    auth_dir = os.path.expanduser("~/.vani_instagram_auth")
    os.makedirs(auth_dir, exist_ok=True)

    try:
        with sync_playwright() as p:
            # Launch persistent context to reuse cookies/login state
            browser = p.chromium.launch_persistent_context(
                user_data_dir=auth_dir,
                headless=False, # Keep visible for login and monitoring
                channel="chrome", # Use actual Chrome if available
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            print("[Instagram Tool] Navigating to Instagram...")
            page.goto("https://www.instagram.com/")

            # Wait to see if we are logged in
            # We look for the "New post" SVG icon or similar navigation item
            # The exact aria-label is usually "New post"
            new_post_svg_selector = 'svg[aria-label="New post"]'
            login_form_selector = 'input[name="username"]'
            
            # Wait up to 5 seconds to see which one appears
            try:
                page.wait_for_selector(f"{new_post_svg_selector}, {login_form_selector}", timeout=5000)
            except Exception:
                pass
            
            if page.locator(login_form_selector).is_visible():
                print("[Instagram Tool] ⚠️ Login required.")
                print("Please log in manually in the browser window. The script will wait until you are logged in...")
                # Wait until the new post button appears (which implies successful login)
                page.wait_for_selector(new_post_svg_selector, timeout=0) # wait indefinitely
                print("[Instagram Tool] Login detected! Proceeding with post...")
            else:
                try:
                    page.wait_for_selector(new_post_svg_selector, timeout=5000)
                except:
                    # If we can't find it, wait a bit longer or tell user
                    print("[Instagram Tool] Couldn't find the 'New post' button, waiting a bit...")
                    page.wait_for_selector(new_post_svg_selector, timeout=30000)

            time.sleep(2) # Give the page a moment to settle

            # Click the New post button
            print("[Instagram Tool] Clicking 'Create' button...")
            page.locator(new_post_svg_selector).first.click()

            # The modal appears. There's usually a "Select from computer" button
            # We intercept the file chooser dialog
            print("[Instagram Tool] Uploading file...")
            with page.expect_file_chooser(timeout=10000) as fc_info:
                # Sometimes it's text, sometimes a button
                page.locator("text=Select from computer").click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            # Wait for Next button (cropping stage)
            print("[Instagram Tool] File selected. Clicking Next (Crop)...")
            # The button is usually text="Next"
            page.locator("text=Next").first.click()
            time.sleep(1)

            # Wait for Next button (filters stage)
            print("[Instagram Tool] Clicking Next (Filters)...")
            page.locator("text=Next").first.click()
            time.sleep(1)

            # Now we are on the caption stage
            print("[Instagram Tool] Writing caption...")
            # The textarea usually has aria-label="Write a caption..."
            caption_textarea = page.locator('div[aria-label="Write a caption..."]')
            caption_textarea.wait_for()
            caption_textarea.fill(caption)
            time.sleep(1)

            # Click Share
            print("[Instagram Tool] Clicking Share...")
            page.locator("text=Share").first.click()

            # Wait for confirmation
            print("[Instagram Tool] Waiting for confirmation...")
            page.locator('text=Your post has been shared.').wait_for(timeout=30000)
            print("[Instagram Tool] Successfully posted!")

            time.sleep(2) # Leave it open for a couple of seconds so user can see it finished
            browser.close()
            return "The post has been successfully shared to Instagram, sir."

    except Exception as e:
        import traceback
        err_msg = str(e)
        print(f"[Instagram Tool] ❌ Error: {err_msg}")
        traceback.print_exc()
        return f"I ran into an issue while trying to post to Instagram. Error details: {err_msg[:100]}..."

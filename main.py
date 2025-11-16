import pandas as pd
import asyncio
import time
import asyncio
from playwright.async_api import async_playwright  
import re
from openai import OpenAI
from keys import OPENAI_API_KEY

def get_by_user_input(craft_data):
    # First remove duplicate projects
    craft_data = craft_data.drop_duplicates(subset=['Project-Title'], keep='first')
    categories = ['3D Printing', 'Arduino', 'Art', 'Boats', 'Books & Journals', 
                'Cardboard', 'Cards', 'Christmas', 'Clay', 'Cleaning', 'Clocks', 'Costumes & Cosplay', 
                'Digital Graphics', 'Duct Tape', 'Embroidery', 'Fashion', 'Felt', 'Fiber Arts', 'Furniture', 'Gift Wrapping', 
                'Halloween', 'Holidays', 'Home Improvement', 'Jewelry', 'Kids', 'Knitting & Crochet', 'Knots', 'Launchers', 
                'Leather', 'Life Hacks', 'Mason Jars', 'Math', 'Metalworking', 'Molds & Casting', 'Music', 'No-Sew', 'Paper', 
                'Parties & Weddings', 'Photography', 'Printmaking', 'Relationships', 'Reuse', 'Science', 'Sewing', 'Soapmaking', 
                'Speakers', 'Tools', 'Toys & Games', 'Wallets', 'Water', 'Wearables', 'Woodworking']

    print("Available Craft Categories:")
    print(categories)

    print("Choose a Category, or press Enter to include all")
    subcategory = input("Category: ")
    if subcategory == "":
        subcategory = None

    print("How many projects do you want to see?")
    number_of_results_input = input("Number (1-20): ")
    number_of_results = int(number_of_results_input)

    choice = input("Enter 1 for most viewed or 2 for most favorited: ")
    if choice == "1":
        sort_by_favorite = False
    else:
        sort_by_favorite = True

    if sort_by_favorite:
        sort_category = "Favorites"
    else:
        sort_category = "Views"

    if subcategory is not None:
        filtered_data = craft_data[craft_data['Subcategory'] == subcategory]
        top_viewed = filtered_data.nlargest(number_of_results, sort_category)
    else:
        top_viewed = craft_data.nlargest(number_of_results, sort_category) 
    
    # CH reindex the resulting DataFrame to have sequential indexes starting from 0
    top_viewed = top_viewed.reset_index(drop=True)

    return top_viewed

async def auto_scroll(page, iterations=12, pause=0.75):
    """Scroll to the bottom repeatedly to trigger lazy-loaded content."""
    last_h = 0

    for i in range(iterations):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(pause)
        print(".", end="", flush=True)  # Print dot for each scroll
        h = await page.evaluate("document.body.scrollHeight")
        if h == last_h:
            print(f" Done!")
            break
        last_h = h
    else:
        print(" Done!")  # If we completed all iterations

async def scrape_URL_for_text(url):
  
    timeout = 60000  # milliseconds
    print("Loading page content", end="", flush=True)  # Start the progress line
    async with async_playwright() as p:
        # Run Playwright locally (no BrowserCat / no wss)
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
        )
        page = await context.new_page()

        # Speed: skip heavy assets that aren't needed for text/HTML extraction
        await context.route("**/*", lambda route: route.abort()
                      if route.request.resource_type in {"image", "media", "font"}
                      else route.continue_())

        # Navigate and wait for the page to quiet down
        await page.goto(url, wait_until="networkidle", timeout=timeout)

        # Try to dismiss any cookie banner (best-effort; ignore errors)
        for selector in [
            "button:has-text('Accept')",
            "button:has-text('I Agree')",
            "text=/accept all cookies/i",
        ]:
            try:
                await page.locator(selector).first.click(timeout=2000)
                break
            except Exception:
                pass

        # Trigger lazy-loaded content
        await auto_scroll(page)

        # 1) Fully rendered HTML (serialized DOM).  <-- "true" HTML after JS runs
        rendered_html = await page.content()

        # 2) Readable text (tags stripped) - try to target the main article first
        selectors = ['article', 'main', '[role=main]', '[itemprop=articleBody]', '.article', '.post', '.entry-content', '.content']
        readable_text = ""
        for s in selectors:
            try:
                el = await page.query_selector(s)
                if el:
                    # Remove all anchor tags from this element before getting text
                    await page.evaluate(f"""
                        document.querySelectorAll('{s} a').forEach(a => a.remove());
                    """)
                    txt = (await el.inner_text() or "").strip()
                    if len(txt) > 100:
                        readable_text = re.sub(r'\n{3,}', '\n\n', txt).strip()
                        break
            except Exception:
                pass

        if not readable_text:
            # Fallback: clone body and remove likely non-article regions (header/footer/nav/aside/sidebar)
            readable_text = await page.evaluate(
                """() => {
                    const clone = document.body.cloneNode(true);
                    const removeSel = ['header','footer','nav','aside','[class*="sidebar"]','[class*="cookie"]','[class*="masthead"]','a'];
                    removeSel.forEach(sel => {
                        clone.querySelectorAll(sel).forEach(n => n.remove());
                    });
                    return (clone.innerText || '').replace(/\\n{3,}/g, '\\n\\n').trim();
                }"""
            )

        # Print to stdout
        #print("\n=== RENDERED HTML ===\n")
        #print(rendered_html)
        #print("\n=== READABLE TEXT ===\n")
        #print(readable_text)

        fname = "data\\" + url.split("/")[-2] + ".txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(readable_text)

        await browser.close()

        return readable_text


def extract_materials_and_instructions(text_content, project_title=""):

    
    # Initialize OpenAI client (make sure to set your API key)
    client = OpenAI(
        api_key=OPENAI_API_KEY  # Set this environment variable
    )
    
    prompt = f"""
    Please analyze the following craft project text and extract the materials and step-by-step instructions.
    
    Format your response as plain text with these two sections:
    
    MATERIALS:
    - List each material needed (one per line with dashes)
    
    INSTRUCTIONS:
    1. List each step numbered (clear, concise steps)
    
    Keep the language clear and concise. Remove any website navigation text, ads, or irrelevant content.
    Only include the essential materials and steps for completing the craft project.
    
    Project text:
    {text_content}
    """
    
    try:
        print("Analyzing text with OpenAI...", end="", flush=True)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts craft project information. Respond with clean, plain text formatting."},
                {"role": "user", "content": prompt}
            ],
            #max_tokens=2000,
            temperature=0.0  # Lower temperature for more consistent extraction
        )
        
        print(" Done!")
        
        # Return the text response directly as a string
        result = response.choices[0].message.content.strip()
        return result
            
    except Exception as e:
        print(f"\nError with OpenAI API: {e}")
        return f"ERROR: {e}"

def get_project(table):
    print(table)
    print("Which project would you like to see more about? Enter the index number")
    index = input("Index:")
    index_num = int(index) # already zero-based due to reset_index earlier
    
    # Get the project title and Instructables link from the table
    project_title = table.iloc[index_num]['Project-Title']
    instructables_link = table.iloc[index_num]['Instructables-link']
    url = f"https://www.instructables.com{instructables_link}"

    return project_title, url


async def scrape_and_analyze(project_title, url):

    
    # Scrape the webpage for text content
    try:
        text_content = await scrape_URL_for_text(url)
        
        if not text_content:
            return "ERROR: No text content could be scraped from the webpage"
            
        # Extract materials and instructions using AI
        analysis_result = extract_materials_and_instructions(text_content, project_title)

        return analysis_result
        
    except Exception as e:
        return f"ERROR: Failed to scrape and analyze the project: {e}"
    
    
def show_intructions(project_name, instructions_text):
    print("\n\nInstructions for", project_name)
    print(instructions_text)
     

# MAIN

craft_data = pd.read_csv(r"data\projects_craft.csv")

# User input/interction
top_viewed = get_by_user_input(craft_data)
project_title, url = get_project(top_viewed)
print(f"Selected project: {project_title}, please be patient while we fetch the instructions...")
instructions_text = asyncio.run(scrape_and_analyze(project_title, url))
show_intructions(project_title, instructions_text)